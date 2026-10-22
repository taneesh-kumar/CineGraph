from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return health status of the CineGraph API."""
    return HealthResponse(
        status="ok",
        service="CineGraph API",
        version="0.1.0",
    )
