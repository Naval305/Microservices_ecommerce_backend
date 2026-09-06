from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "product_service"
    API_V1_PREFIX: str = "/api/v1"
    DB_CONNECTION_STRING: str
    DB_NAME: str
    REDIS_CONNECTION_STRING: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
