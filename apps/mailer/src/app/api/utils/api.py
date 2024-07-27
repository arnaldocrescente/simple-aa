from fastapi import APIRouter

from app.api.utils.endpoints import health

utils_router = APIRouter(tags=["internal"])
utils_router.include_router(health.router)
