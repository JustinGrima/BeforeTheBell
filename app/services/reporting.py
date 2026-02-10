from __future__ import annotations

import csv
from datetime import date
from io import StringIO
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Job, JobAttempt, Staff


def build_daily_summary(db: Session, for_date: date) -> str:
    jobs = db.execute(select(Job).where(Job.job_date == for_date)).scalars().all()
    lines = [f"Daily Cover Summary for {for_date}"]
    for job in jobs:
        absent = db.get(Staff, job.absent_teacher_id)
        supply = db.get(Staff, job.assigned_supply_id) if job.assigned_supply_id else None
        lines.append(
            f"Job {job.id}: absent={absent.name if absent else '-'} supply={supply.name if supply else 'UNRESOLVED'} "
            f"{job.start_time}-{job.end_time} {job.subject} status={job.status.value}"
        )
        lines.append(f"absence transcript: {job.absence_transcript}")
        for att in db.execute(select(JobAttempt).where(JobAttempt.job_id == job.id)).scalars().all():
            lines.append(
                f"attempt {att.attempt_type.value} seq={att.sequence_num} outcome={att.outcome.value}"
                f" body={att.message_body or ''} response={att.response_text or ''}"
            )
    return "\n".join(lines)


def build_payroll_csv(db: Session, for_date: date) -> str:
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["date", "type", "job_id", "staff_id", "teacher_name", "hours", "subject", "cost_centre"],
    )
    writer.writeheader()

    jobs = db.execute(select(Job).where(Job.job_date == for_date)).scalars().all()
    for job in jobs:
        absent = db.get(Staff, job.absent_teacher_id)
        supply = db.get(Staff, job.assigned_supply_id) if job.assigned_supply_id else None
        hours = round((job.end_time.hour + job.end_time.minute / 60) - (job.start_time.hour + job.start_time.minute / 60), 2)
        writer.writerow(
            {
                "date": str(job.job_date),
                "type": "time_off",
                "job_id": job.id,
                "staff_id": absent.id,
                "teacher_name": absent.name,
                "hours": hours,
                "subject": job.subject,
                "cost_centre": absent.cost_centre,
            }
        )
        if supply:
            writer.writerow(
                {
                    "date": str(job.job_date),
                    "type": "supply_pay",
                    "job_id": job.id,
                    "staff_id": supply.id,
                    "teacher_name": supply.name,
                    "hours": hours,
                    "subject": job.subject,
                    "cost_centre": supply.cost_centre,
                }
            )

    return output.getvalue()
