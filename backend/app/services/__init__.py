from app.services.recommendation_service import RecommendationService
from app.services.analytics_service import AnalyticsService
from app.repositories import get_neo4j_repo, get_monetdb_repo


def get_recommendation_service() -> RecommendationService:
    """FastAPI dependency for RecommendationService."""
    return RecommendationService(neo4j_repo=get_neo4j_repo())


def get_analytics_service() -> AnalyticsService:
    """FastAPI dependency for AnalyticsService."""
    return AnalyticsService(monetdb_repo=get_monetdb_repo())


__all__ = [
    "RecommendationService",
    "AnalyticsService",
    "get_recommendation_service",
    "get_analytics_service",
]
