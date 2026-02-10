from datetime import date, time
import uuid

from app.db.session import SessionLocal
from app.models.entities import AttemptOutcome, AttemptType, Job, JobAttempt, JobStatus, Staff
from app.services.dispatch import dispatch_job


def run() -> None:
    with SessionLocal() as db:
        absent = db.query(Staff).filter(Staff.role == "absent").first()
        supply1 = db.query(Staff).filter(Staff.role == "supply", Staff.priority == 1).first()
        supply2 = db.query(Staff).filter(Staff.role == "supply", Staff.priority == 2).first()

        job1 = Job(
            school_id=absent.school_id,
            absent_teacher_id=absent.id,
            job_date=date.today(),
            start_time=time(8, 30),
            end_time=time(15, 0),
            subject="Math",
            notes="simulation accept path",
            absence_transcript="2026-01-01 08:30-15:00 Math",
            status=JobStatus.pending,
            correlation_id=str(uuid.uuid4()),
        )
        db.add(job1)
        db.commit()
        db.add(JobAttempt(job_id=job1.id, supply_teacher_id=supply1.id, attempt_type=AttemptType.call, sequence_num=42, outcome=AttemptOutcome.accepted, response_text="yes"))
        db.commit()
        dispatch_job(db, job1.id)
        print(f"accept-path job={job1.id} status={db.get(Job, job1.id).status.value}")

        job2 = Job(
            school_id=absent.school_id,
            absent_teacher_id=absent.id,
            job_date=date.today(),
            start_time=time(8, 30),
            end_time=time(15, 0),
            subject="Science",
            notes="simulation decline then accept",
            absence_transcript="2026-01-01 08:30-15:00 Science",
            status=JobStatus.pending,
            correlation_id=str(uuid.uuid4()),
        )
        db.add(job2)
        db.commit()
        db.add(JobAttempt(job_id=job2.id, supply_teacher_id=supply1.id, attempt_type=AttemptType.call, sequence_num=1, outcome=AttemptOutcome.declined, response_text="no"))
        db.add(JobAttempt(job_id=job2.id, supply_teacher_id=supply2.id, attempt_type=AttemptType.sms, sequence_num=1, outcome=AttemptOutcome.accepted, response_text="yes"))
        db.commit()
        dispatch_job(db, job2.id)
        print(f"decline-then-accept job={job2.id} assigned_supply={db.get(Job, job2.id).assigned_supply_id}")


if __name__ == "__main__":
    run()
