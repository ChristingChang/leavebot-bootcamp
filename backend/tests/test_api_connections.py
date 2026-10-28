from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app.main import app


def test_concurrent_requests_do_not_fail_when_closing_connection(db_path):
    # 同步 yield dependency 的前後兩段可能在不同執行緒跑；並行請求會讓這種情況必然出現。
    with TestClient(app, raise_server_exceptions=False) as client:
        with ThreadPoolExecutor(max_workers=20) as pool:
            codes = list(pool.map(lambda _: client.get("/api/employees").status_code, range(100)))

    assert codes == [200] * 100
