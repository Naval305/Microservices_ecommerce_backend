from typing import Any

from app.db.session import get_client
from app.schemas.custom_response import APIResponse
from fastapi import APIRouter, Depends
from fastapi.logger import logger
from pymongo.errors import PyMongoError

router = APIRouter(prefix="/server", tags=["server"])


@router.get("/healthz")
async def health_check() -> APIResponse[Any]:
    return APIResponse()


@router.get("/readyz")
async def ready_check(client=Depends(get_client)) -> APIResponse[Any]:
    try:
        await client.admin.command("ping")
        return APIResponse()
    except PyMongoError:
        logger.exception("DB readiness check failed")
        return APIResponse(success=False, message="Not ready")
