import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.core.exceptions import *

logger: logging.Logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s", request.url)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "data": None},
    )


async def parent_category_not_found_handler(
    request: Request,
    exc: ParentCategoryNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Parent category does not exist",
            "data": None,
        },
    )


async def category_exists_handler(
    request: Request,
    exc: CategoryExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"success": False, "message": "Category already exists", "data": None},
    )


async def category_not_exists(
    request: Request,
    exc: CategoryNotExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"success": False, "message": "Category does not exists", "data": None},
    )


async def same_category_parent_error(
    request: Request,
    exc: SameCategoryParentError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"success": False, "message": "A category cannot be its own parent", "data": None},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers all custom exception handlers to the FastAPI application."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(
        ParentCategoryNotFoundError, parent_category_not_found_handler
    )
    app.add_exception_handler(CategoryExistsError, category_exists_handler)
    app.add_exception_handler(CategoryNotExistsError, category_not_exists)
    app.add_exception_handler(SameCategoryParentError, same_category_parent_error)
