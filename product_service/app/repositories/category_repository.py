from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult


class CategoryRepository:
    def __init__(self, db) -> None:
        self.db: AsyncDatabase = db

    async def get_many(self, query: dict) -> list:
        return await self.db.category.find(query).to_list(length=None)

    async def get_by_id(self, category_id: str) -> dict | None:
        return await self.db.category.find_one({"_id": ObjectId(category_id)})

    async def get_by_name(self, category_name: str) -> dict | None:
        return await self.db.category.find_one({"name": category_name})

    async def _find_one(self, query: dict) -> dict | None:
        return await self.db.category.find_one(query)

    async def create(self, data: dict) -> dict:
        result: InsertOneResult = await self.db.category.insert_one(data)
        return await self.db.category.find_one({"_id": result.inserted_id})

    async def update_by_id(self, category_id: str, update: dict) -> dict | None:
        return await self.db.category.find_one_and_update(
            {"_id": ObjectId(category_id)},
            {"$set": update},
            return_document=ReturnDocument.AFTER,
        )

    async def update_many_by_query(
        self, query: dict, update: dict, operation: str = "$set"
    ) -> int:
        result: UpdateResult = await self.db.category.update_many(
            query, {operation: update}
        )
        return result.modified_count

    async def delete(self, category_id: str) -> int:
        result: DeleteResult = await self.db.category.delete_one(
            {"_id": ObjectId(category_id)}
        )
        return result.deleted_count
