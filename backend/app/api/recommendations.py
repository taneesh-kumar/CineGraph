import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from app.services import RecommendationService, get_recommendation_service
from app.schemas.services import RecommendationResult

logger = logging.getLogger("cinegraph-recommendations-api")

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get(
    "/movie/{movie_id}",
    response_model=RecommendationResult,
    summary="Get similar movie recommendations",
    description=(
        "Returns explainable graph-based movie recommendations sharing genres and rating evidence "
        "with the specified MovieLens movie ID. The source movie is strictly excluded."
    ),
)
async def get_similar_movies(
    movie_id: Annotated[int, Path(ge=1, description="Target MovieLens movie ID")],
    limit: Annotated[
        int, Query(ge=1, le=50, description="Maximum number of recommendations to return")
    ] = 10,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResult:
    """Return similar movies for a specified movie ID."""
    return service.get_similar_movies(movie_id=movie_id, limit=limit)


@router.get(
    "/user/{user_id}",
    response_model=RecommendationResult,
    summary="Get personalized user recommendations",
    description=(
        "Returns personalized movie recommendations for a specified user ID using collaborative "
        "filtering signals from peer rating patterns. Movies already rated by the user are strictly excluded."
    ),
)
async def get_user_recommendations(
    user_id: Annotated[int, Path(ge=1, description="Target MovieLens user ID")],
    limit: Annotated[
        int, Query(ge=1, le=50, description="Maximum number of recommendations to return")
    ] = 10,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResult:
    """Return personalized recommendations for a specified user ID."""
    return service.get_user_recommendations(user_id=user_id, limit=limit)
