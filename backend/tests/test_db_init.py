from app import db


def test_init_db_twice_keeps_three_seed_employees(db_path):
    db.init_db(db_path)
    db.init_db(db_path)

    conn = db.connect(db_path)
    try:
        assert db.list_employees(conn) == [
            {"id": "E001", "name": "王小明"},
            {"id": "E002", "name": "李小華"},
            {"id": "E003", "name": "陳小美"},
        ]
        assert conn.execute("SELECT COUNT(*) FROM leave_requests").fetchone()[0] == 0
    finally:
        conn.close()


def test_get_db_path_reads_env_at_call_time(db_path, monkeypatch):
    assert db.get_db_path() == db_path

    other = db_path.parent / "other.db"
    monkeypatch.setenv("LEAVEBOT_DB", str(other))
    assert db.get_db_path() == other


def test_lifespan_initializes_temp_db(client, db_path):
    assert db_path.exists()
