from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.extensions.redis_connection import redis_client


def init_rate_limiter(app):
    global limiter
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=app.config["REDIS_URL"],
        storage_options={"connection_pool": redis_client.connection_pool},
        strategy="fixed-window",
        default_limits=["200 per minute", "1000 per hour"],
        swallow_errors=True,
    )
    limiter.init_app(app)


def get_login_email_key():
    try:
        data = request.get_json(silent=True) or {}
        email = data.get("email", "").strip().lower()
        return f"email:{email}" if email else get_remote_address()
    except Exception:
        return get_remote_address()
