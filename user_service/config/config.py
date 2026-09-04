import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    DEBUG = False
    TESTING = False

    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB, adjust to taste

    PRIVATE_KEY_PATH = BASE_DIR / "keys" / "private.pem"
    PUBLIC_KEY_PATH = BASE_DIR / "keys" / "public.pem"
    REFRESH_SECRET_KEY = os.environ["REFRESH_SECRET_KEY"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_TITLE = "User Service API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/api-docs"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
    REDIS_SOCKET_CONNECT_TIMEOUT = float(os.environ.get("REDIS_SOCKET_CONNECT_TIMEOUT", 2))
    REDIS_SOCKET_TIMEOUT = float(os.environ.get("REDIS_SOCKET_TIMEOUT", 2))
    REDIS_MAX_CONNECTIONS = int(os.environ.get("REDIS_MAX_CONNECTIONS", 20))
    _redis_auth = f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""
    REDIS_URL = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

class DevelopmentConfig(Config):
    DEBUG = True
    os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'db' / os.getenv('DB_NAME', 'user_service')}.db"

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'db' / os.getenv('DB_NAME', 'user_service')}.db"


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