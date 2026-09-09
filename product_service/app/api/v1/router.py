from app.api.v1.endpoints import category, products, server
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(products.router)
api_router.include_router(category.router)
api_router.include_router(server.router)
