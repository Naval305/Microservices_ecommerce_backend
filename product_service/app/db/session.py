from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import settings

MONGO_DETAILS: str = settings.DB_CONNECTION_STRING

client = AsyncMongoClient(settings.DB_CONNECTION_STRING)
db = client[settings.DB_NAME]


def get_db() -> AsyncDatabase:
    return db
