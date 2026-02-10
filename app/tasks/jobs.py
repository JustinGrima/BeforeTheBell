from datetime import date

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.dispatch import dispatch_job
from app.services.notify import notify_admins, send_email
from app.services.reporting import build_daily_summary, build_payroll_csv
from app.tasks.celery_app import celery_app


@celery_app.task
def process_job(job_id: int) -> None:
    with SessionLocal() as db:
        dispatch_job(db, job_id)


@celery_app.task
def send_daily_reports() -> None:
    today = date.today()
    with SessionLocal() as db:
        summary = build_daily_summary(db, today)
        csv_content = build_payroll_csv(db, today)

    send_email(f"BeforeTheBell Summary {today}", summary, [e.strip() for e in settings.admin_emails.split(",") if e.strip()])
    send_email(
        f"BeforeTheBell Payroll Export {today}",
        f"CSV attached below\n\n{csv_content}",
        [e.strip() for e in settings.admin_emails.split(",") if e.strip()],
    )
    notify_admins("Daily reports sent", f"Summary and payroll export sent for {today}")
