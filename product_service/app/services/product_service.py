from typing import Any

from app.core.exceptions import (
    CategoryNotExistsError,
    ProductExistsError,
    ProductNotExistsError,
)
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schemas import ProductCreate, ProductUpdate
from app.services.category_service import CategoryService
from app.utils.helpers import PyObjectId, generate_sku


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self.repository: ProductRepository = repository

    async def get_all_products(self) -> list[Any]:
        return await self.repository.get_many({})

    async def get_product_by_sku(self, sku) -> dict | None:
        return await self.repository.get_by_sku(sku)

    async def create_product(
        self, data: ProductCreate, cat_service: CategoryService
    ) -> dict:
        category_id: PyObjectId = data.category_id
        data.sku = await generate_sku(category_id)

        product_with_category = await self.repository.get_many(
            {"name": data.name, "category_id": category_id}
        )
        if product_with_category:
            raise ProductExistsError

        product_by_sku: dict | None = await self.get_product_by_sku(data.sku)
        if product_by_sku:
            raise ProductExistsError

        if category_id:
            category_exists: (
                dict[Any, Any] | None
            ) = await cat_service.get_category_by_id(category_id)
            if not category_exists:
                raise CategoryNotExistsError

        return await self.repository.create(data.model_dump(mode="json"))

    async def update_product(
        self, sku: str, data: ProductUpdate, cat_service: CategoryService
    ) -> dict[Any, Any] | None:
        category_id: PyObjectId | None = data.category_id

        product_by_sku: dict | None = await self.get_product_by_sku(sku)
        if not product_by_sku:
            raise ProductNotExistsError

        if category_id:
            category_exists: (
                dict[Any, Any] | None
            ) = await cat_service.get_category_by_id(category_id)
            if not category_exists:
                raise CategoryNotExistsError

        return await self.repository.update_by_sku(
            sku, data.model_dump(exclude_unset=True)
        )

    async def delete_product(self, sku: str) -> int:
        product_by_sku: dict | None = await self.get_product_by_sku(sku)
        if not product_by_sku:
            raise ProductNotExistsError

        return await self.repository.delete(sku)
