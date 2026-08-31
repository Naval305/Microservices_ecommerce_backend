
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import db_host, db_port, db_name, db_user, db_password, cluster_name

MONGO_DETAILS = f"mongodb+srv://{db_user}:{db_password}@{db_host}/?appName={cluster_name}"

client = AsyncIOMotorClient(MONGO_DETAILS)

db = client[db_name]
