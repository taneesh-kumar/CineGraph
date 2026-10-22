from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.health import router as health_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CineGraph Backend API combining Neo4j graph recommendations and MonetDB analytical queries.",
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint identifying the CineGraph API."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "description": "CineGraph NoSQL hybrid graph and analytical backend",
        "docs_url": "/docs",
    }
