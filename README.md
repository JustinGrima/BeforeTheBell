# BeforeTheBell (MVP)

Voice and SMS substitute teacher dispatcher built with FastAPI, Postgres, Redis, and Celery.

## Features
- Inbound absence intake via Twilio SMS webhook.
- Deterministic sequential dispatch ladder (call -> sms -> call) with stop conditions.
- Audit trail for call/SMS attempts, responses, and timestamps.
- Idempotent webhook handling via unique webhook keys.
- Daily summary + payroll CSV generation.
- Admin notifications via SMTP email (and optional SMS).

## Stack
- Python + FastAPI
- Postgres + SQLAlchemy + Alembic
- Redis + Celery worker/beat
- Twilio REST API + TwiML

## Quick start
1. Copy env template:
   ```bash
   cp .env.example .env
   ```
2. Build and start services:
   ```bash
   docker compose up --build -d
   ```
3. Run migrations:
   ```bash
   docker compose exec api alembic upgrade head
   ```
4. Seed demo data:
   ```bash
   docker compose exec api python -m app.cli.seed
   ```
5. Start using webhooks:
   - `POST /twilio/sms/absence`
   - `POST /twilio/voice/answer`
   - `POST /twilio/voice/result`
   - `POST /twilio/sms/reply`
   - `POST /twilio/status/call`

## Local (without Docker)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests
```bash
pytest
```

## Simulation script
```bash
python scripts/simulate.py
```

## Sample daily summary email body
```
Daily Cover Summary for 2026-01-01
Job 1: absent=Alice Absent supply=Sam Supply 08:30:00-15:00:00 Math status=filled
absence transcript: 2026-01-01 08:30-15:00 Math
attempt call seq=1 outcome=accepted body=... response=yes
```

## Sample payroll CSV
```csv
date,type,job_id,staff_id,teacher_name,hours,subject,cost_centre
2026-01-01,time_off,1,1,Alice Absent,6.5,Math,SCI
2026-01-01,supply_pay,1,3,Sam Supply,6.5,Math,GEN
```

## Twilio config notes
- Configure inbound SMS webhook to `/twilio/sms/absence`.
- Configure outbound call `url` to `/twilio/voice/answer`.
- Configure call status callback to `/twilio/status/call`.
- Configure supply SMS replies webhook to `/twilio/sms/reply`.

## Reliability notes
- Webhook idempotency via `processed_webhooks` unique key.
- Job processing guarded by DB row lock (`FOR UPDATE SKIP LOCKED`).
- Supply double-booking protection with unique constraint on assignment time window.
