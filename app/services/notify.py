import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.services.twilio_client import send_sms


def send_email(subject: str, body: str, recipients: list[str]) -> None:
    msg = EmailMessage()
    msg["From"] = settings.smtp_sender
    msg["To"] = ",".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(msg)


def notify_admins(subject: str, body: str) -> None:
    emails = [e.strip() for e in settings.admin_emails.split(",") if e.strip()]
    if emails:
        send_email(subject, body, emails)

    sms_numbers = [n.strip() for n in settings.admin_sms_numbers.split(",") if n.strip()]
    for number in sms_numbers:
        send_sms(number, f"{subject}: {body[:120]}")
