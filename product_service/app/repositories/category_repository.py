from pymongo.asynchronous.database import AsyncDatabase


class CategoryRepository:
    def __init__(self, db) -> None:
        self.db: AsyncDatabase = db

    async def get_all(self) -> list:
        return await self.db.category.find({}).to_list(length=None)
