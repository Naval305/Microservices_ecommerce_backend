from typing import Any

from bson import ObjectId

from app.core.exceptions import (
    CategoryExistsError,
    CategoryNotExistsError,
    ParentCategoryNotFoundError,
    SameCategoryParentError,
)
from app.repositories.category_repository import CategoryRepository
from app.schemas.category_schemas import CategoryCreateSchema, CategoryUpdateSchema


class CategoryService:
    def __init__(self, repository: CategoryRepository) -> None:
        self.repository: CategoryRepository = repository

    async def get_all_categories(self) -> list[Any]:
        return await self.repository.get_many({})

    async def get_category_by_id(self, category_id) -> dict[Any, Any] | None:
        return await self.repository.get_by_id(category_id)

    async def get_category_by_name(self, name) -> dict[Any, Any] | None:
        return await self.repository.get_by_name(name)

    async def get_ancestors(self, parent_id) -> list[Any]:
        ancestors = []

        if parent_id:
            parent: dict[Any, Any] | None = await self.get_category_by_id(parent_id)

            if not parent:
                raise ParentCategoryNotFoundError

            ancestors = parent.get("ancestors", []) + [str(parent["_id"])]
        return ancestors

    async def create_category(
        self,
        data: CategoryCreateSchema,
    ) -> dict:
        category_exists: dict[Any, Any] | None = await self.get_category_by_name(
            data.name
        )
        if category_exists:
            raise CategoryExistsError

        ancestors: list[Any] = await self.get_ancestors(data.parent_id)
        doc = {
            "name": data.name,
            "is_active": data.is_active,
            "parent_id": data.parent_id,
            "ancestors": ancestors,
        }

        return await self.repository.create(doc)

    async def update_category(
        self, category_id: str, data: CategoryUpdateSchema
    ) -> dict[Any, Any] | None:
        category: dict[Any, Any] | None = await self.get_category_by_id(category_id)
        if not category:
            raise CategoryNotExistsError

        if data.parent_id:
            if data.parent_id == category_id:
                raise SameCategoryParentError

            parent_category: dict[Any, Any] | None = await self.repository.get_by_id(
                data.parent_id
            )
            if not parent_category:
                raise CategoryNotExistsError

            descendant = await self.repository._find_one(
                {"_id": ObjectId(data.parent_id), "ancestors": category_id}
            )
            if descendant:
                raise ValueError(
                    "Cannot set a descendant as parent (would create a cycle)"
                )

            new_ancestors: list[Any] = await self.get_ancestors(data.parent_id)
            await self.repository.update_by_id(
                category_id, {"ancestors": new_ancestors}
            )

            new_prefix: list[Any] = new_ancestors + [category_id]
            all_descendants = await self.repository.get_many({"ancestors": category_id})

            for child in all_descendants:
                old_ancestors = child["ancestors"]
                idx = old_ancestors.index(category_id)
                relative_tail = old_ancestors[
                    idx + 1 :
                ]  # path from category_id down to this child, unchanged
                child_new_ancestors = new_prefix + relative_tail
                await self.repository.update_by_id(
                    str(child["_id"]), {"ancestors": child_new_ancestors}
                )

        return await self.repository.update_by_id(
            category_id, data.model_dump(exclude_unset=True)
        )

    async def delete_category(self, category_id: str) -> int:
        category: dict[Any, Any] | None = await self.repository.get_by_id(category_id)

        if not category:
            raise CategoryNotExistsError

        await self.repository.update_many_by_query(
            {"parent_id": category_id}, {"parent_id": category["parent_id"]}
        )
        await self.repository.update_many_by_query(
            {"ancestors": category_id}, {"ancestors": category_id}, operation="$pull"
        )
        return await self.repository.delete(category_id)
