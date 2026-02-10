from app.models.entities import AttemptOutcome, AttemptType, JobAttempt, JobStatus, Staff
from app.services.dispatch import dispatch_job


def test_dispatch_accepts_when_existing_yes_response(db_session, job):
    supply = db_session.query(Staff).filter(Staff.role == "supply", Staff.priority == 1).first()
    db_session.add(JobAttempt(
        job_id=job.id,
        supply_teacher_id=supply.id,
        attempt_type=AttemptType.sms,
        sequence_num=1,
        outcome=AttemptOutcome.accepted,
        response_text="YES",
    ))
    db_session.commit()

    dispatch_job(db_session, job.id)
    db_session.refresh(job)
    assert job.status == JobStatus.filled


def test_dispatch_fails_when_no_responses(db_session, job):
    dispatch_job(db_session, job.id)
    db_session.refresh(job)
    assert job.status == JobStatus.failed
