import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import get_db_manager
from app.core.exceptions import (
    CineGraphException,
    EntityNotFoundException,
    DatabaseConnectionException,
    DatabaseQueryException,
    InvalidInputException,
)
from app.api.health import router as health_router
from app.api.recommendations import router as recommendations_router
from app.api.analytics import router as analytics_router
from app.api.movies import router as movies_router

logger = logging.getLogger("cinegraph-api")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager:
    Safely cleans up database connection pools and resources on shutdown.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    yield
    logger.info("Shutting down CineGraph API, closing database connections...")
    db_manager = get_db_manager()
    db_manager.close_neo4j_driver()
    logger.info("All database drivers closed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CineGraph Backend API combining Neo4j graph recommendations and MonetDB analytical queries.",
    lifespan=lifespan,
)

# ------------------------------------------------------------------------------
# Exception Handlers
# ------------------------------------------------------------------------------
@app.exception_handler(EntityNotFoundException)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
    logger.info(f"Entity not found: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "message": exc.message},
    )


@app.exception_handler(InvalidInputException)
async def invalid_input_handler(request: Request, exc: InvalidInputException):
    logger.warning(f"Invalid input: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad Request", "message": exc.message},
    )


@app.exception_handler(DatabaseConnectionException)
async def db_connection_handler(request: Request, exc: DatabaseConnectionException):
    logger.error(f"Database connection error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": "Database Unavailable", "message": f"Connection to {exc.database} is currently unavailable."},
    )


@app.exception_handler(DatabaseQueryException)
async def db_query_handler(request: Request, exc: DatabaseQueryException):
    logger.error(f"Database query error on {exc.database}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Database Error", "message": "An error occurred while querying the database."},
    )


@app.exception_handler(CineGraphException)
async def generic_cinegraph_handler(request: Request, exc: CineGraphException):
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Application Error", "message": exc.message},
    )


# ------------------------------------------------------------------------------
# CORS Middleware setup
# ------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Router Registration (Both root & /api/v1 compatible)
# ------------------------------------------------------------------------------
# 1. Root & backward-compatible health checks
app.include_router(health_router)

# 2. Versioned API prefix (/api/v1)
app.include_router(health_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(movies_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint identifying the CineGraph API."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "description": "CineGraph NoSQL hybrid graph and analytical backend",
        "docs_url": "/docs",
        "api_v1_prefix": "/api/v1",
    }
