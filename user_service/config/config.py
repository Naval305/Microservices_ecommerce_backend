import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = False
    TESTING = False

    PRIVATE_KEY = Path("keys/private.pem").read_text()
    PUBLIC_KEY = Path("keys/public.pem").read_text()
    REFRESH_SECRET_KEY = os.environ["REFRESH_SECRET_KEY"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_TITLE = "User Service API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.getenv('DB_NAME', 'app')}.db"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.getenv('DB_NAME', 'app')}.db"


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