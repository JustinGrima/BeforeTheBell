from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import ProcessedWebhook


def register_webhook(db: Session, source: str, external_id: str) -> bool:
    marker = ProcessedWebhook(source=source, external_id=external_id)
    db.add(marker)
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
