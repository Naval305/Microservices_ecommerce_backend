from typing import Any

from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository: CategoryRepository = repository

    async def get_category(self) -> list[Any]:
        return await self.repository.get_all()
