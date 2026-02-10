"""init

Revision ID: 0001_init
Revises:
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("schools",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
    )
    op.create_table("staff",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("school_id", sa.Integer(), sa.ForeignKey("schools.id"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("phone_e164", sa.String(length=32), nullable=False, unique=True),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.Integer()),
        sa.Column("cost_centre", sa.String(length=64), server_default="GEN", nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    job_status = sa.Enum("pending", "filled", "failed", name="jobstatus")
    job_status.create(op.get_bind())
    op.create_table("jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("school_id", sa.Integer(), sa.ForeignKey("schools.id"), nullable=False),
        sa.Column("absent_teacher_id", sa.Integer(), sa.ForeignKey("staff.id"), nullable=False),
        sa.Column("assigned_supply_id", sa.Integer(), sa.ForeignKey("staff.id")),
        sa.Column("status", job_status, nullable=False),
        sa.Column("job_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("subject", sa.String(length=120), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("absence_transcript", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("filled_at", sa.DateTime()),
        sa.Column("escalated_at", sa.DateTime()),
        sa.Column("correlation_id", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("school_id", "assigned_supply_id", "job_date", "start_time", "end_time", name="uq_supply_booking"),
    )

    attempt_type = sa.Enum("call", "sms", name="attempttype")
    attempt_outcome = sa.Enum("accepted", "declined", "no_answer", "timeout", "failed", name="attemptoutcome")
    attempt_type.create(op.get_bind())
    attempt_outcome.create(op.get_bind())

    op.create_table("job_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("job_id", sa.Integer(), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("supply_teacher_id", sa.Integer(), sa.ForeignKey("staff.id"), nullable=False),
        sa.Column("attempt_type", attempt_type, nullable=False),
        sa.Column("sequence_num", sa.Integer(), nullable=False),
        sa.Column("twilio_sid", sa.String(length=64)),
        sa.Column("message_body", sa.Text()),
        sa.Column("response_text", sa.Text()),
        sa.Column("speech_transcript", sa.Text()),
        sa.Column("outcome", attempt_outcome, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("responded_at", sa.DateTime()),
    )

    op.create_table("processed_webhooks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("source", "external_id", name="uq_webhook_idempotency"),
    )


def downgrade() -> None:
    op.drop_table("processed_webhooks")
    op.drop_table("job_attempts")
    op.drop_table("jobs")
    op.drop_table("staff")
    op.drop_table("schools")
