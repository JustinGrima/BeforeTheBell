from app.services.parsing import parse_absence_sms, parse_yes_no


def test_parse_absence_sms():
    result = parse_absence_sms("2026-01-01 08:00-15:00 Math notes:Need plans")
    assert result["subject"] == "Math"
    assert result["notes"] == "Need plans"


def test_parse_yes_no():
    assert parse_yes_no("YES") == "yes"
    assert parse_yes_no("2") == "no"
    assert parse_yes_no("maybe") is None
