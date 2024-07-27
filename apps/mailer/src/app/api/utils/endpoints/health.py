from fastapi import APIRouter

from app.schema import HealthStatus

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
def health_check() -> HealthStatus:
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
