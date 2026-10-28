from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_is_served_at_root():
    with TestClient(app) as client:
        index = client.get("/")

    assert index.status_code == 200
    assert "text/html" in index.headers["content-type"]
