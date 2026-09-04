"""Application logging configuration and HTTP access logging."""

from __future__ import annotations

import logging
import logging.config
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from flask import Flask, g, request


def configure_logging(app: Flask) -> None:
    """Configure one consistent logger for the app and its dependencies."""
    level = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    log_file = Path(app.config.get("LOG_FILE", "")) if app.config.get("LOG_FILE") else None

    handlers: dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        }
    }
    handler_names = ["console"]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "standard",
            "filename": str(log_file),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        }
        handler_names.append("file")

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                }
            },
            "filters": {"request_context": {"()": RequestContextFilter}},
            "handlers": {
                name: {**handler, "filters": ["request_context"]}
                for name, handler in handlers.items()
            },
            "root": {"level": level, "handlers": handler_names},
        }
    )
    app.logger.setLevel(level)

    @app.before_request
    def start_request() -> None:
        g.request_id = request.headers.get("X-Request-ID", str(uuid4()))
        g.request_started_at = time.perf_counter()

    @app.after_request
    def log_request(response):
        elapsed_ms = (time.perf_counter() - g.request_started_at) * 1000
        app.logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        response.headers["X-Request-ID"] = g.request_id
        return response


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(g, "request_id", "-") if _has_request_context() else "-"
        return True


def _has_request_context() -> bool:
    try:
        from flask import has_request_context

        return has_request_context()
    except RuntimeError:
        return False
