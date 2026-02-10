from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_absence_webhook_unknown_teacher():
    response = client.post(
        "/twilio/sms/absence",
        data={"MessageSid": "SMX1", "From": "+19999999999", "Body": "2026-01-01 08:00-15:00 Math"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "unknown_teacher"
