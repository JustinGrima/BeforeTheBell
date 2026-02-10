from app.db.session import SessionLocal
from app.models.entities import School, Staff


def run() -> None:
    with SessionLocal() as db:
        school = School(name="Demo School", timezone="America/Toronto")
        db.add(school)
        db.flush()

        db.add_all(
            [
                Staff(school_id=school.id, name="Alice Absent", phone_e164="+15550000001", role="absent", cost_centre="SCI"),
                Staff(school_id=school.id, name="Bob Absent", phone_e164="+15550000002", role="absent", cost_centre="MTH"),
                Staff(school_id=school.id, name="Sam Supply", phone_e164="+15550000101", role="supply", priority=1),
                Staff(school_id=school.id, name="Sally Supply", phone_e164="+15550000102", role="supply", priority=2),
                Staff(school_id=school.id, name="Sean Supply", phone_e164="+15550000103", role="supply", priority=3),
                Staff(school_id=school.id, name="Sara Supply", phone_e164="+15550000104", role="supply", priority=4),
                Staff(school_id=school.id, name="Sid Supply", phone_e164="+15550000105", role="supply", priority=5),
            ]
        )
        db.commit()


if __name__ == "__main__":
    run()
