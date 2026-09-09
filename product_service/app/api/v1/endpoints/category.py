from typing import Any

from app.api.dependencies import get_category_service
from app.schemas.category_schemas import (
    CategoryCreateSchema,
    CategoryOut,
    CategoryUpdateSchema,
)
from app.schemas.custom_response import APIResponse
from app.services.category_service import CategoryService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/category", tags=["category"])


@router.get("/list", response_model=APIResponse[list[CategoryOut]])
async def get_categories(
    service: CategoryService = Depends(get_category_service),
) -> APIResponse[list[CategoryOut]]:
    return APIResponse(data=await service.get_all_categories())


@router.post("/create", response_model=APIResponse[CategoryOut])
async def create_category(
    data: CategoryCreateSchema,
    service: CategoryService = Depends(get_category_service),
) -> APIResponse[dict]:
    return APIResponse(data=await service.create_category(data))


@router.patch("/update/{category_id}", response_model=APIResponse[CategoryOut])
async def update_category(
    category_id: str,
    data: CategoryUpdateSchema,
    service: CategoryService = Depends(get_category_service),
) -> APIResponse[dict]:
    return APIResponse(data=await service.update_category(category_id, data))


@router.delete("/delete/{category_id}")
async def delete_category(
    category_id: str, service: CategoryService = Depends(get_category_service)
) -> APIResponse[dict]:
    deleted_count: int = await service.delete_category(category_id)
    return APIResponse(
        message="Category deleted successfully",
        data={"deleted_count": deleted_count},
    )
