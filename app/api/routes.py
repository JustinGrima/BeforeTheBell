from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from twilio.twiml.voice_response import Gather, VoiceResponse

from app.db.session import get_db
from app.models.entities import AttemptOutcome, AttemptType, Job, JobAttempt, JobStatus, Staff
from app.services.idempotency import register_webhook
from app.services.parsing import parse_absence_sms, parse_yes_no
from app.tasks.jobs import process_job

router = APIRouter()


@router.post("/twilio/sms/absence")
def inbound_absence_sms(
    MessageSid: str = Form(...),
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db),
):
    if not register_webhook(db, "absence_sms", MessageSid):
        return {"status": "duplicate"}

    teacher = db.execute(select(Staff).where(Staff.phone_e164 == From, Staff.role == "absent")).scalar_one_or_none()
    if not teacher:
        return {"status": "unknown_teacher"}

    parsed = parse_absence_sms(Body)
    job = Job(
        school_id=teacher.school_id,
        absent_teacher_id=teacher.id,
        status=JobStatus.pending,
        absence_transcript=Body,
        correlation_id=str(uuid.uuid4()),
        **parsed,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    process_job.delay(job.id)
    return {"status": "created", "job_id": job.id}


@router.post("/twilio/voice/answer", response_class=PlainTextResponse)
def voice_answer(job_id: int, supply_id: int):
    vr = VoiceResponse()
    gather = Gather(input="speech dtmf", timeout=5, num_digits=1, action=f"/twilio/voice/result?job_id={job_id}&supply_id={supply_id}", method="POST")
    gather.say("CoverCall AI. Job available. Say yes to accept, no to decline. Press 1 for yes, 2 for no.")
    vr.append(gather)
    vr.say("Sorry, I did not catch that. Goodbye.")
    return str(vr)


@router.post("/twilio/voice/result", response_class=PlainTextResponse)
def voice_result(
    job_id: int,
    supply_id: int,
    SpeechResult: str | None = Form(None),
    Digits: str | None = Form(None),
    db: Session = Depends(get_db),
):
    response_text = Digits or SpeechResult
    decision = parse_yes_no(response_text)
    outcome = AttemptOutcome.accepted if decision == "yes" else AttemptOutcome.declined if decision == "no" else AttemptOutcome.no_answer

    db.add(
        JobAttempt(
            job_id=job_id,
            supply_teacher_id=supply_id,
            attempt_type=AttemptType.call,
            sequence_num=99,
            outcome=outcome,
            response_text=response_text,
            speech_transcript=SpeechResult,
            responded_at=datetime.utcnow(),
        )
    )
    db.commit()

    vr = VoiceResponse()
    if decision == "yes":
        vr.say("Thank you. You are confirmed.")
    elif decision == "no":
        vr.say("Thank you. We will contact someone else.")
    else:
        vr.say("No clear response. Goodbye.")
    return str(vr)


@router.post("/twilio/sms/reply")
def supply_sms_reply(
    MessageSid: str = Form(...),
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db),
):
    if not register_webhook(db, "supply_reply", MessageSid):
        return {"status": "duplicate"}

    supply = db.execute(select(Staff).where(Staff.phone_e164 == From, Staff.role == "supply")).scalar_one_or_none()
    if not supply:
        return {"status": "unknown_supply"}

    pending_job = db.execute(
        select(Job)
        .where(Job.status == JobStatus.pending, Job.school_id == supply.school_id)
        .order_by(Job.created_at.asc())
    ).scalar_one_or_none()
    if not pending_job:
        return {"status": "no_pending_job"}

    outcome = AttemptOutcome.accepted if parse_yes_no(Body) == "yes" else AttemptOutcome.declined
    db.add(
        JobAttempt(
            job_id=pending_job.id,
            supply_teacher_id=supply.id,
            attempt_type=AttemptType.sms,
            sequence_num=2,
            outcome=outcome,
            response_text=Body,
            responded_at=datetime.utcnow(),
        )
    )
    db.commit()
    return {"status": "recorded"}


@router.post("/twilio/status/call")
def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    db: Session = Depends(get_db),
):
    attempt = db.execute(select(JobAttempt).where(JobAttempt.twilio_sid == CallSid)).scalar_one_or_none()
    if not attempt:
        return {"status": "unknown_call"}
    if CallStatus in {"failed", "busy", "no-answer"}:
        attempt.outcome = AttemptOutcome.no_answer
    db.commit()
    return {"status": "ok"}
