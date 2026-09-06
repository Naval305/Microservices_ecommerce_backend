from fastapi import APIRouter

catergory_router = APIRouter()

from app.apis.v1.catergory_apis import router

catergory_router.include_router(router, prefix="/category", tags=["Categories"])