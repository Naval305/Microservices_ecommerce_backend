from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.results import DeleteResult, UpdateResult


class ProductRepository:
    def __init__(self, db) -> None:
        self.db: AsyncDatabase = db

    async def get_many(self, query: dict) -> list:
        return await self.db.products.find(query).to_list(length=None)

    async def get_by_sku(self, sku: str) -> dict | None:
        return await self.db.products.find_one({"sku": sku})

    async def create(self, data: dict) -> dict:
        await self.db.products.insert_one(data)
        return data

    async def update_by_sku(self, sku: str, update: dict) -> dict | None:
        return await self.db.products.find_one_and_update(
            {"sku": sku},
            {"$set": update},
            return_document=ReturnDocument.AFTER,
        )

    async def update_many_by_query(
        self, query: dict, update: dict, operation: str = "$set"
    ) -> int:
        result: UpdateResult = await self.db.products.update_many(
            query, {operation: update}
        )
        return result.modified_count

    async def delete(self, sku: str) -> int:
        result: DeleteResult = await self.db.products.delete_one({"sku": sku})
        return result.deleted_count
