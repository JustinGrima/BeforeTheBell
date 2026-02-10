import logging
import uuid


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s correlation_id=%(correlation_id)s %(message)s",
    )


class CorrelationAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        correlation_id = self.extra.get("correlation_id") or str(uuid.uuid4())
        kwargs.setdefault("extra", {})
        kwargs["extra"]["correlation_id"] = correlation_id
        return msg, kwargs


def get_logger(name: str, correlation_id: str | None = None) -> CorrelationAdapter:
    return CorrelationAdapter(logging.getLogger(name), {"correlation_id": correlation_id})
