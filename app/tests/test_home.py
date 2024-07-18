from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("api/v1/")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}
