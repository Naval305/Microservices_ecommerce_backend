
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import (
    cluster_name,
    db_host,
    db_name,
    db_password,
    db_user,
)

MONGO_DETAILS = f"mongodb+srv://{db_user}:{db_password}@{db_host}/?appName={cluster_name}"

client = AsyncIOMotorClient(MONGO_DETAILS)

db = client[db_name]
