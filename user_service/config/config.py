import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    DEBUG = False
    TESTING = False

    PRIVATE_KEY_PATH = BASE_DIR / "keys" / "private.pem"
    PUBLIC_KEY_PATH = BASE_DIR / "keys" / "public.pem"
    REFRESH_SECRET_KEY = os.environ["REFRESH_SECRET_KEY"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_TITLE = "User Service API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"

    REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

class DevelopmentConfig(Config):
    DEBUG = True
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

if os.getenv("APP_ENV") == "development":
    os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"