import os
from collections.abc import Generator
from typing import Any

os.environ["DB_CONNECTION_STRING"] = "mongodb://test.invalid:27017"
os.environ["DB_NAME"] = "product_service_tests"
os.environ["REDIS_CONNECTION_STRING"] = "redis://test.invalid:6379/0"

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.api.dependencies import get_category_service, get_product_service
from app.db.session import get_client
from app.main import app
from app.services.category_service import CategoryService
from app.services.product_service import ProductService


class MemoryProductRepository:
    def __init__(self) -> None:
        self.products: dict[str, dict[str, Any]] = {}

    async def get_many(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            product
            for product in self.products.values()
            if all(product.get(key) == value for key, value in query.items())
        ]

    async def get_by_sku(self, sku: str) -> dict[str, Any] | None:
        return self.products.get(sku)

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        data.setdefault("_id", ObjectId())
        self.products[data["sku"]] = data
        return data

    async def update_by_sku(
        self, sku: str, update: dict[str, Any]
    ) -> dict[str, Any] | None:
        product = self.products.get(sku)
        if product:
            product.update(update)
        return product

    async def delete(self, sku: str) -> int:
        return int(self.products.pop(sku, None) is not None)


class MemoryCategoryRepository:
    def __init__(self) -> None:
        self.categories: dict[str, dict[str, Any]] = {}

    async def get_many(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        if not query:
            return list(self.categories.values())
        if set(query) == {"ancestors"}:
            return [
                category
                for category in self.categories.values()
                if query["ancestors"] in category.get("ancestors", [])
            ]
        return [
            category
            for category in self.categories.values()
            if all(category.get(key) == value for key, value in query.items())
        ]

    async def get_by_id(self, category_id: str) -> dict[str, Any] | None:
        return self.categories.get(str(category_id))

    async def get_by_name(self, category_name: str) -> dict[str, Any] | None:
        return next(
            (
                category
                for category in self.categories.values()
                if category["name"] == category_name
            ),
            None,
        )

    async def _find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        category = self.categories.get(str(query.get("_id", "")))
        if category and query.get("ancestors") in category.get("ancestors", []):
            return category
        return None

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        data.setdefault("_id", ObjectId())
        self.categories[str(data["_id"])] = data
        return data

    async def update_by_id(
        self, category_id: str, update: dict[str, Any]
    ) -> dict[str, Any] | None:
        category = self.categories.get(category_id)
        if category:
            category.update(update)
        return category

    async def update_many_by_query(
        self, query: dict[str, Any], update: dict[str, Any], operation: str = "$set"
    ) -> int:
        matches = await self.get_many(query)
        for category in matches:
            for key, value in update.items():
                if operation == "$pull":
                    category[key] = [item for item in category[key] if item != value]
                else:
                    category[key] = value
        return len(matches)

    async def delete(self, category_id: str) -> int:
        return int(self.categories.pop(category_id, None) is not None)


class ReadyClient:
    class Admin:
        async def command(self, command: str) -> None:
            assert command == "ping"

    admin = Admin()


@pytest.fixture
def client() -> Generator[TestClient]:
    product_repository = MemoryProductRepository()
    category_repository = MemoryCategoryRepository()
    app.dependency_overrides = {
        get_product_service: lambda: ProductService(product_repository),
        get_category_service: lambda: CategoryService(category_repository),
        get_client: lambda: ReadyClient(),
    }

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()
