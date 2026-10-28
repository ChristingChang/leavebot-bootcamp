import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def db_path(tmp_path):
    # 每個測試都用自己的暫存資料庫，連沒用 client fixture 的測試也不會碰開發資料庫。
    # 用獨立的 MonkeyPatch：測試裡呼叫 monkeypatch.undo() 也不會把路徑還原成開發資料庫（缺陷 D-2）。
    path = tmp_path / "test.db"
    with pytest.MonkeyPatch.context() as env:
        env.setenv("LEAVEBOT_DB", str(path))
        yield path


@pytest.fixture
def client(db_path):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_payload():
    # Test Plan「合法基底」；每次回傳新的 dict，測試可自由修改。
    return {
        "employee_id": "E001",
        "leave_type": "annual",
        "start_date": "2026-10-16",
        "end_date": "2026-10-19",
        "period": "full_day",
        "reason": "",
    }
