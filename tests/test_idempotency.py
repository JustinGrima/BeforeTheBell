from app.services.idempotency import register_webhook


def test_webhook_idempotency(db_session):
    assert register_webhook(db_session, "absence_sms", "SM123") is True
    assert register_webhook(db_session, "absence_sms", "SM123") is False
