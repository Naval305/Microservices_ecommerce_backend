from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies import get_category_service
from app.schemas.category_schemas import (
    CategoryOut,
)
from app.schemas.custom_response import APIResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/category", tags=["category"])

# @router.get("/create", response_model=APIResponse[list[CategoryOut]])
# async def create_category(data: CategoryCreateSchema, db) -> dict:
#     ancestors = []
#     if data.parent_id:
#         parent = await db.categories.find_one({"_id": ObjectId(data.parent_id)})
#         if not parent:
#             raise ValueError("Parent category does not exist")
#         ancestors = parent.get("ancestors", []) + [str(parent["_id"])]

#     doc = {
#         "name": data.name,
#         "is_active": data.is_active,
#         "parent_id": data.parent_id,
#         "ancestors": ancestors,
#     }
#     result = await db.categories.insert_one(doc)
#     return await db.categories.find_one({"_id": result.inserted_id})


# async def update_category(category_id: str, data: CategoryUpdateSchema, db) -> dict:
#     if data.parent_id:
#         # cycle check: new parent can't be the category itself or one of its own descendants
#         if data.parent_id == category_id:
#             raise ValueError("A category cannot be its own parent")

#         descendant = await db.categories.find_one({
#             "_id": ObjectId(data.parent_id),
#             "ancestors": category_id,
#         })
#         if descendant:
#             raise ValueError("Cannot set a descendant as parent (would create a cycle)")

#     # ... apply update, and if parent_id changed, recompute ancestors for this
#     # category AND cascade-update ancestors for all its descendants


@router.get("/list", response_model=APIResponse[list[CategoryOut]])
async def get_categories(
    service: CategoryService = Depends(get_category_service),
) -> APIResponse[Any]:
    return APIResponse(data=await service.get_category())
