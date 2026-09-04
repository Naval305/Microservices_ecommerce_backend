"""Celery extension setup without import-time Flask configuration access."""

from __future__ import annotations

from typing import Any

from celery import Celery, Task
from flask import Flask

celery_app = Celery("user_service")


class FlaskContextTask(Task):
    """Run tasks inside the Flask application context."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        with self.app.flask_app.app_context():  # type: ignore[attr-defined]
            return self.run(*args, **kwargs)


def init_celery(app: Flask) -> Celery:
    """Configure Celery from an already-created Flask application."""
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.flask_app = app  # type: ignore[attr-defined]
    celery_app.Task = FlaskContextTask
    app.extensions["celery"] = celery_app
    return celery_app

