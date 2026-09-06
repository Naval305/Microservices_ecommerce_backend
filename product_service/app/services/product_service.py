from typing import Any

from app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository: ProductRepository = repository

    async def get_products(self) -> list[Any]:
        return await self.repository.get_all()
