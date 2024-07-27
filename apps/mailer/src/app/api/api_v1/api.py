from fastapi import APIRouter

from app.api.api_v1.endpoints import mailer

api_router = APIRouter()
api_router.include_router(mailer.router, tags=["mailer"])
