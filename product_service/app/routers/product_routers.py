from fastapi import APIRouter

product_router = APIRouter()

from app.apis.v1.product_apis import router

product_router.include_router(router, prefix="/products", tags=["Products"])
