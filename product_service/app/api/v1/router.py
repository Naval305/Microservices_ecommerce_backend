from fastapi import APIRouter

from app.api.v1.endpoints import category, products

api_router = APIRouter()
api_router.include_router(products.router)
api_router.include_router(category.router)
