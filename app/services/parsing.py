from datetime import datetime
import re


ABSENCE_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<start>\d{2}:\d{2})-(?P<end>\d{2}:\d{2})\s+(?P<subject>[\w\s]+?)(?:\s+notes:(?P<notes>.*))?$",
    re.IGNORECASE,
)


def parse_absence_sms(body: str) -> dict:
    """Expected format: 2026-09-15 08:30-15:00 Math notes:Doctor appointment"""
    match = ABSENCE_PATTERN.search(body.strip())
    if not match:
        raise ValueError("Invalid absence format")
    return {
        "job_date": datetime.strptime(match.group("date"), "%Y-%m-%d").date(),
        "start_time": datetime.strptime(match.group("start"), "%H:%M").time(),
        "end_time": datetime.strptime(match.group("end"), "%H:%M").time(),
        "subject": match.group("subject").strip(),
        "notes": (match.group("notes") or "").strip(),
    }


def parse_yes_no(text: str | None) -> str | None:
    if not text:
        return None
    normalized = text.strip().lower()
    if normalized in {"yes", "y", "1", "accept"}:
        return "yes"
    if normalized in {"no", "n", "2", "decline"}:
        return "no"
    return None
