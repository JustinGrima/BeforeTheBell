from datetime import date, time
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.entities import Job, JobStatus, School, Staff


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, future=True)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        school = School(name="Test School", timezone="America/Toronto")
        db.add(school)
        db.flush()
        db.add_all([
            Staff(school_id=school.id, name="Absent", phone_e164="+10000000001", role="absent"),
            Staff(school_id=school.id, name="Supply 1", phone_e164="+10000000002", role="supply", priority=1),
            Staff(school_id=school.id, name="Supply 2", phone_e164="+10000000003", role="supply", priority=2),
        ])
        db.commit()
        yield db


@pytest.fixture()
def job(db_session):
    absent = db_session.query(Staff).filter(Staff.role == "absent").first()
    job = Job(
        school_id=absent.school_id,
        absent_teacher_id=absent.id,
        status=JobStatus.pending,
        job_date=date(2026, 1, 1),
        start_time=time(8, 0),
        end_time=time(15, 0),
        subject="Math",
        notes="",
        absence_transcript="2026-01-01 08:00-15:00 Math",
        correlation_id=str(uuid.uuid4()),
    )
    db_session.add(job)
    db_session.commit()
    return job
