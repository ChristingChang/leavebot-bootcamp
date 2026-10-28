import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "leavebot.db"

SEED_EMPLOYEES = (
    ("E001", "王小明"),
    ("E002", "李小華"),
    ("E003", "陳小美"),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT NOT NULL REFERENCES employees(id),
    leave_type TEXT NOT NULL CHECK (leave_type IN ('annual', 'personal', 'sick')),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL CHECK (end_date >= start_date),
    period TEXT NOT NULL CHECK (period IN ('full_day', 'am', 'pm')),
    reason TEXT NOT NULL DEFAULT '',
    days REAL NOT NULL CHECK (days > 0),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status = 'pending')
);
"""


def get_db_path() -> Path:
    # 每次呼叫才讀環境變數，讓測試可以在匯入之後替換路徑。
    value = os.environ.get("LEAVEBOT_DB")
    if value:
        return Path(value)
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DEFAULT_DB_PATH


def connect(path) -> sqlite3.Connection:
    # FastAPI 的同步 yield dependency 可能在不同執行緒開啟與關閉連線；
    # 每條連線只屬於一個請求、不會被同時使用，所以關掉同執行緒檢查是安全的。
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path) -> None:
    conn = connect(path)
    try:
        with conn:
            conn.executescript(SCHEMA)
            conn.executemany(
                "INSERT OR IGNORE INTO employees (id, name) VALUES (?, ?)",
                SEED_EMPLOYEES,
            )
    finally:
        conn.close()


def list_employees(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT id, name FROM employees ORDER BY id").fetchall()
    return [dict(row) for row in rows]


def list_employee_ids(conn: sqlite3.Connection) -> set[str]:
    return {row["id"] for row in conn.execute("SELECT id FROM employees")}


def insert_leave(conn: sqlite3.Connection, leave: dict) -> dict:
    with conn:
        cursor = conn.execute(
            "INSERT INTO leave_requests"
            " (employee_id, leave_type, start_date, end_date, period, reason, days, status)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                leave["employee_id"],
                leave["leave_type"],
                leave["start_date"],
                leave["end_date"],
                leave["period"],
                leave["reason"],
                leave["days"],
                leave["status"],
            ),
        )
    return {**leave, "id": cursor.lastrowid}


def list_leaves(conn: sqlite3.Connection, employee_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id, employee_id, leave_type, start_date, end_date, period, reason, days, status"
        " FROM leave_requests WHERE employee_id = ? ORDER BY id DESC",
        (employee_id,),
    ).fetchall()
    return [dict(row) for row in rows]
