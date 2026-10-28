import sqlite3

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app import db, leave_rules

router = APIRouter(prefix="/api")


def get_conn():
    # 每個請求一條連線；以 db.xxx 呼叫，測試才能替換 db 的函式。
    conn = db.connect(db.get_db_path())
    try:
        yield conn
    finally:
        conn.close()


def error_response(status_code: int, field, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"errors": [{"field": field, "code": code, "message": message}]},
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/employees")
def list_employees(conn: sqlite3.Connection = Depends(get_conn)):
    try:
        employees = db.list_employees(conn)
    except sqlite3.Error:
        return error_response(500, None, "database_error", "系統暫時無法讀取資料，請稍後再試")
    return {"employees": employees}


@router.post("/leaves")
async def create_leave(request: Request, conn: sqlite3.Connection = Depends(get_conn)):
    # 本文不是 JSON 物件時直接回 400，不做後續檢查（SDS API-03 驗證順序 1）。
    try:
        payload = await request.json()
    except ValueError:
        payload = None
    if not isinstance(payload, dict):
        return error_response(400, None, "invalid_body", "請求格式錯誤")
    try:
        result = leave_rules.validate_leave_request(payload, db.list_employee_ids(conn))
        if result.errors:
            return JSONResponse(status_code=422, content={"errors": result.errors})
        leave = db.insert_leave(conn, result.leave)
    except sqlite3.Error:
        # 不回傳例外內容，避免把 SQL 或檔案路徑露給使用者。
        return error_response(500, None, "database_error", "系統暫時無法處理，資料沒有存檔，請稍後再試")
    return JSONResponse(status_code=201, content={"leave": leave})


@router.get("/employees/{employee_id}/leaves")
def list_leaves(employee_id: str, conn: sqlite3.Connection = Depends(get_conn)):
    if employee_id not in db.list_employee_ids(conn):
        return error_response(404, "employee_id", "employee_not_found", "找不到這位員工")
    return {"leaves": db.list_leaves(conn, employee_id)}
