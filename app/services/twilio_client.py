from twilio.rest import Client

from app.core.config import settings


def get_client() -> Client:
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


def place_call(to_number: str, status_callback: str, url: str) -> str:
    if not settings.twilio_account_sid:
        return "mock-call-sid"
    call = get_client().calls.create(
        to=to_number,
        from_=settings.twilio_from_number,
        url=url,
        status_callback=status_callback,
        status_callback_event=["initiated", "ringing", "answered", "completed"],
        method="POST",
    )
    return call.sid


def send_sms(to_number: str, body: str) -> str:
    if not settings.twilio_account_sid:
        return "mock-sms-sid"
    msg = get_client().messages.create(to=to_number, from_=settings.twilio_from_number, body=body)
    return msg.sid
