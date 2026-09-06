from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies import get_product_service
from app.schemas.custom_response import APIResponse
from app.schemas.product_schemas import ProductOut
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/list", response_model=APIResponse[list[ProductOut]])
async def get_products(
    service: ProductService = Depends(get_product_service),
) -> APIResponse[Any]:
    return APIResponse(data=await service.get_products())
