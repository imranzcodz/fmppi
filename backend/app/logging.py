import json
import logging
import sys
from typing import Any

from app.config import settings


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


class PIIRedactingFormatter(logging.Formatter):
    SENSITIVE_FIELDS = {"password", "password_hash", "secret", "token", "refresh_token", "mfa_secret"}

    def _redact(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {k: ("***" if k.lower() in self.SENSITIVE_FIELDS else self._redact(v)) for k, v in value.items()}
        if isinstance(value, list | tuple):
            return [self._redact(v) for v in value]
        return value

    def format(self, record: logging.LogRecord) -> str:
        if isinstance(record.msg, dict):
            record.msg = self._redact(record.msg)
        return super().format(record)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIDFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn").propagate = True
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
