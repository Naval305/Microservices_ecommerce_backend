from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
register_exception_handlers(app)
