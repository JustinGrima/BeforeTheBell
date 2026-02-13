from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_homepage_serves_monday_clone_layout():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Marketing Sprint Board" in response.text
    assert "monday" in response.text
    assert "clone" in response.text
