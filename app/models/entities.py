from __future__ import annotations

from datetime import datetime, date, time
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class JobStatus(str, Enum):
    pending = "pending"
    filled = "filled"
    failed = "failed"


class AttemptType(str, Enum):
    call = "call"
    sms = "sms"


class AttemptOutcome(str, Enum):
    accepted = "accepted"
    declined = "declined"
    no_answer = "no_answer"
    timeout = "timeout"
    failed = "failed"


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), nullable=False)


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone_e164: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # absent/supply/admin
    priority: Mapped[int | None] = mapped_column(Integer)
    cost_centre: Mapped[str] = mapped_column(String(64), default="GEN")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)
    absent_teacher_id: Mapped[int] = mapped_column(ForeignKey("staff.id"), nullable=False)
    assigned_supply_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id"))
    status: Mapped[JobStatus] = mapped_column(SAEnum(JobStatus), default=JobStatus.pending, nullable=False)

    job_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    absence_transcript: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at: Mapped[datetime | None] = mapped_column(DateTime)
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("school_id", "assigned_supply_id", "job_date", "start_time", "end_time", name="uq_supply_booking"),
    )

    attempts: Mapped[list[JobAttempt]] = relationship(back_populates="job")


class JobAttempt(Base):
    __tablename__ = "job_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    supply_teacher_id: Mapped[int] = mapped_column(ForeignKey("staff.id"), nullable=False)
    attempt_type: Mapped[AttemptType] = mapped_column(SAEnum(AttemptType), nullable=False)
    sequence_num: Mapped[int] = mapped_column(Integer, nullable=False)
    twilio_sid: Mapped[str | None] = mapped_column(String(64))
    message_body: Mapped[str | None] = mapped_column(Text)
    response_text: Mapped[str | None] = mapped_column(Text)
    speech_transcript: Mapped[str | None] = mapped_column(Text)
    outcome: Mapped[AttemptOutcome] = mapped_column(SAEnum(AttemptOutcome), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime)

    job: Mapped[Job] = relationship(back_populates="attempts")


class ProcessedWebhook(Base):
    __tablename__ = "processed_webhooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_webhook_idempotency"),)
