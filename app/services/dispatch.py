from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.models.entities import AttemptOutcome, AttemptType, Job, JobAttempt, JobStatus, Staff
from app.services.parsing import parse_yes_no
from app.services.twilio_client import place_call, send_sms

VOICE_SCRIPT = (
    "BeforeTheBell. A teaching job is available. Say yes to accept or no to decline. "
    "You can also press 1 to accept or 2 to decline."
)


def lock_job(db: Session, job_id: int) -> Job | None:
    stmt = select(Job).where(Job.id == job_id).with_for_update(skip_locked=True)
    return db.execute(stmt).scalar_one_or_none()


def dispatch_job(db: Session, job_id: int) -> None:
    job = lock_job(db, job_id)
    if not job or job.status != JobStatus.pending:
        return

    log = get_logger("dispatch", correlation_id=job.correlation_id)
    start = datetime.utcnow()

    supplies = db.execute(
        select(Staff)
        .where(Staff.school_id == job.school_id, Staff.role == "supply", Staff.active.is_(True))
        .order_by(Staff.priority.asc())
    ).scalars().all()

    for supply in supplies:
        if datetime.utcnow() - start > timedelta(minutes=settings.max_dispatch_minutes):
            job.status = JobStatus.failed
            job.escalated_at = datetime.utcnow()
            db.commit()
            log.info("max elapsed reached")
            return

        call_sid = place_call(
            to_number=supply.phone_e164,
            status_callback=f"{settings.base_url}/twilio/status/call",
            url=f"{settings.base_url}/twilio/voice/answer?job_id={job.id}&supply_id={supply.id}",
        )
        db.add(JobAttempt(
            job_id=job.id,
            supply_teacher_id=supply.id,
            attempt_type=AttemptType.call,
            sequence_num=1,
            twilio_sid=call_sid,
            outcome=AttemptOutcome.no_answer,
            message_body=VOICE_SCRIPT,
        ))
        db.commit()

        decision = get_pending_decision(db, job.id, supply.id)
        if decision == "yes":
            mark_filled(db, job, supply.id)
            log.info("job accepted by call")
            return
        if decision == "no":
            continue

        sms_sid = send_sms(supply.phone_e164, f"Job {job.id}: reply YES to accept or NO to decline.")
        db.add(JobAttempt(
            job_id=job.id,
            supply_teacher_id=supply.id,
            attempt_type=AttemptType.sms,
            sequence_num=1,
            twilio_sid=sms_sid,
            outcome=AttemptOutcome.timeout,
            message_body="Reply YES/NO",
        ))
        db.commit()

        decision = get_pending_decision(db, job.id, supply.id)
        if decision == "yes":
            mark_filled(db, job, supply.id)
            log.info("job accepted by sms")
            return
        if decision == "no":
            continue

        call_sid_2 = place_call(
            to_number=supply.phone_e164,
            status_callback=f"{settings.base_url}/twilio/status/call",
            url=f"{settings.base_url}/twilio/voice/answer?job_id={job.id}&supply_id={supply.id}",
        )
        db.add(JobAttempt(
            job_id=job.id,
            supply_teacher_id=supply.id,
            attempt_type=AttemptType.call,
            sequence_num=2,
            twilio_sid=call_sid_2,
            outcome=AttemptOutcome.no_answer,
            message_body=VOICE_SCRIPT,
        ))
        db.commit()

        if get_pending_decision(db, job.id, supply.id) == "yes":
            mark_filled(db, job, supply.id)
            log.info("job accepted by second call")
            return

    job.status = JobStatus.failed
    job.escalated_at = datetime.utcnow()
    db.commit()
    log.info("supply list exhausted")


def get_pending_decision(db: Session, job_id: int, supply_id: int) -> str | None:
    attempts = db.execute(
        select(JobAttempt)
        .where(JobAttempt.job_id == job_id, JobAttempt.supply_teacher_id == supply_id)
        .order_by(JobAttempt.created_at.desc())
    ).scalars().all()
    for attempt in attempts:
        parsed = parse_yes_no(attempt.response_text)
        if parsed:
            return parsed
    return None


def mark_filled(db: Session, job: Job, supply_id: int) -> None:
    job.assigned_supply_id = supply_id
    job.status = JobStatus.filled
    job.filled_at = datetime.utcnow()
    db.commit()
