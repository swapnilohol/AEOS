from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_v1_health_check() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["success"] is True
