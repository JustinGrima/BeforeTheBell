from datetime import date, time
import uuid

from app.models.entities import Job, JobStatus, Staff
from app.services.reporting import build_payroll_csv


def test_csv_export_contains_time_off_and_supply(db_session):
    absent = db_session.query(Staff).filter(Staff.role == "absent").first()
    supply = db_session.query(Staff).filter(Staff.role == "supply").first()
    job = Job(
        school_id=absent.school_id,
        absent_teacher_id=absent.id,
        assigned_supply_id=supply.id,
        status=JobStatus.filled,
        job_date=date(2026, 1, 1),
        start_time=time(8, 0),
        end_time=time(12, 0),
        subject="Science",
        notes="",
        absence_transcript="text",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(job)
    db_session.commit()

    csv_data = build_payroll_csv(db_session, date(2026, 1, 1))
    assert "time_off" in csv_data
    assert "supply_pay" in csv_data
