from typing import Any

from app.api.dependencies import get_category_service, get_product_service
from app.schemas.custom_response import APIResponse
from app.schemas.product_schemas import ProductCreate, ProductOut, ProductUpdate
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/list", response_model=APIResponse[list[ProductOut]])
async def get_products(
    service: ProductService = Depends(get_product_service),
) -> APIResponse[list[ProductOut]]:
    return APIResponse(data=await service.get_all_products())


@router.post("/create", response_model=APIResponse[ProductOut])
async def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_product_service),
    cat_service: CategoryService = Depends(get_category_service),
) -> APIResponse[dict]:
    return APIResponse(data=await service.create_product(data, cat_service))


@router.patch("/update/{sku}", response_model=APIResponse[ProductOut])
async def update_product(
    sku: str,
    data: ProductUpdate,
    service: ProductService = Depends(get_product_service),
    cat_service: CategoryService = Depends(get_category_service),
) -> APIResponse[dict]:
    return APIResponse(data=await service.update_product(sku, data, cat_service))


@router.delete("/delete/{sku}")
async def delete_product(
    sku: str, service: ProductService = Depends(get_product_service)
) -> APIResponse[dict]:
    deleted_count: int = await service.delete_product(sku)
    return APIResponse(
        message="Product deleted successfully",
        data={"deleted_count": deleted_count},
    )
