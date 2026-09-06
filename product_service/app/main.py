from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import http_exception_handler, unhandled_exception_handler

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
