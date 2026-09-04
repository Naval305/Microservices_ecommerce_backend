import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent


class Config:
    DEBUG = False
    TESTING = False

    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB, adjust to taste
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str | None = f"{BASE_DIR / 'Logs' / (os.getenv('LOG_FILE'))}" if os.getenv("LOG_FILE") else None

    PRIVATE_KEY_PATH: Path = BASE_DIR / "keys" / "private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "keys" / "public.pem"
    REFRESH_SECRET_KEY: str = os.environ["REFRESH_SECRET_KEY"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_TITLE = "User Service API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX: str = "/api-docs"
    OPENAPI_SWAGGER_UI_PATH: str = "/docs"
    OPENAPI_SWAGGER_UI_URL: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    REDIS_HOST: str = os.environ.get("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.environ.get("REDIS_DB", 0))
    REDIS_BROKER_DB: int = int(os.environ.get("REDIS_BROKER_DB", 1))
    REDIS_BACKEND_DB: int = int(os.environ.get("REDIS_BACKEND_DB", 2))
    REDIS_PASSWORD: str | None = os.environ.get("REDIS_PASSWORD") or None
    REDIS_SOCKET_CONNECT_TIMEOUT: float = float(os.environ.get("REDIS_SOCKET_CONNECT_TIMEOUT", 2))
    REDIS_SOCKET_TIMEOUT: float = float(os.environ.get("REDIS_SOCKET_TIMEOUT", 2))
    REDIS_MAX_CONNECTIONS: int = int(os.environ.get("REDIS_MAX_CONNECTIONS", 20))
    _redis_auth: str = f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""
    REDIS_URL: str = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    REDIS_BROKER_URL: str = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}"
    REDIS_BACKEND_URL: str = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_BACKEND_DB}"

    CELERY = {
        "broker_url": REDIS_BROKER_URL,
        "result_backend": REDIS_BACKEND_URL,
        "task_ignore_result": True,   # set False only for tasks you'll poll results on
        "task_track_started": True,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "timezone": "UTC",
        "broker_connection_retry_on_startup": True,
    }

    SEND_MAILS: bool = os.getenv("SEND_MAILS", "true") == "true"
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 1025))
    MAIL_USE_TLS: bool = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME: str | None = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str = os.getenv("MAIL_DEFAULT_SENDER", "no-reply@yourapp.local")

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
    os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"
    SQLALCHEMY_DATABASE_URI: str = (
        f"sqlite:///{BASE_DIR / 'db' / os.getenv('DB_NAME', 'user_service')}.db"
    )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI: str = (
        f"sqlite:///{BASE_DIR / 'db' / os.getenv('DB_NAME', 'user_service')}.db"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


configs = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}

app_config = configs.get(
    os.getenv("APP_ENV", "production"),
    ProductionConfig,
)
