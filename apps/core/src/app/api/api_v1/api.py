from fastapi import APIRouter

from app.api.api_v1.endpoints import accounting, authentication

api_router = APIRouter()
api_router.include_router(authentication.router, tags=["authentication"])
api_router.include_router(accounting.router, tags=["accounting"])
