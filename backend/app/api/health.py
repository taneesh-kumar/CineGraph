import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.database import DatabaseManager, get_db_manager
from app.schemas.common import (
    HealthResponse,
    ReadinessResponse,
    DatabaseStatus,
)

logger = logging.getLogger("cinegraph-health-api")
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Application liveness probe:
    Confirms the API server process is running and responding.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(
    db_manager: DatabaseManager = Depends(get_db_manager),
):
    """
    Database readiness probe:
    Independently verifies connectivity to Neo4j and MonetDB.
    Returns HTTP 200 if both are available, HTTP 503 if either database is down.
    Never exposes credentials or internal stack traces.
    """
    neo4j_ok = db_manager.check_neo4j_health()
    monetdb_ok = db_manager.check_monetdb_health()

    overall_status = "ready" if (neo4j_ok and monetdb_ok) else "unavailable"

    response_payload = {
        "status": overall_status,
        "neo4j": {
            "status": "connected" if neo4j_ok else "unavailable",
            "details": None,
        },
        "monetdb": {
            "status": "connected" if monetdb_ok else "unavailable",
            "details": None,
        },
    }

    status_code = status.HTTP_200_OK if overall_status == "ready" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=response_payload)
