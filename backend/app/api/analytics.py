import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, Path, Query
from app.services import AnalyticsService, get_analytics_service
from app.schemas.services import (
    TopRatedMovie,
    GenrePopularity,
    RatingDistributionItem,
    DatasetSummary,
)
from app.schemas.common import MovieRatingStats

logger = logging.getLogger("cinegraph-analytics-api")

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/top-rated",
    response_model=List[TopRatedMovie],
    summary="Get top-rated movies",
    description=(
        "Returns top-rated movies computed directly in MonetDB, using a minimum rating count threshold "
        "to prevent low-sample skew. Enriched with release years and genres."
    ),
)
async def get_top_rated_movies(
    min_ratings: Annotated[
        int, Query(ge=1, le=10000, description="Minimum number of ratings required")
    ] = 10,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of movies to return")
    ] = 20,
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[TopRatedMovie]:
    """Return top-rated movies meeting a minimum rating threshold."""
    return service.get_top_rated_movies(min_ratings=min_ratings, limit=limit)


@router.get(
    "/genres",
    response_model=List[GenrePopularity],
    summary="Get genre popularity metrics",
    description=(
        "Returns aggregate rating activity per genre, including total rating events, count of distinct "
        "movies rated, and average rating calculated in MonetDB."
    ),
)
async def get_genre_popularity(
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[GenrePopularity]:
    """Return genre popularity and aggregate rating activity."""
    return service.get_genre_popularity()


@router.get(
    "/ratings/distribution",
    response_model=List[RatingDistributionItem],
    summary="Get rating distribution",
    description=(
        "Returns the discrete frequency distribution and percentage share across all MovieLens ratings "
        "(0.5 to 5.0 in 0.5 increments)."
    ),
)
async def get_rating_distribution(
    service: AnalyticsService = Depends(get_analytics_service),
) -> List[RatingDistributionItem]:
    """Return rating score frequency distribution and percentage share."""
    return service.get_rating_distribution()


@router.get(
    "/movies/{movie_id}/ratings",
    response_model=MovieRatingStats,
    summary="Get movie rating statistics",
    description="Returns aggregate rating count and average rating for a specified MovieLens movie ID.",
)
async def get_movie_rating_stats(
    movie_id: Annotated[int, Path(ge=1, description="Target MovieLens movie ID")],
    service: AnalyticsService = Depends(get_analytics_service),
) -> MovieRatingStats:
    """Return average rating and rating count for a specific movie."""
    return service.get_movie_stats(movie_id=movie_id)


@router.get(
    "/summary",
    response_model=DatasetSummary,
    summary="Get dataset summary counts",
    description="Returns global database counts of movies, users, genres, ratings, and tags from MonetDB.",
)
async def get_dataset_summary(
    service: AnalyticsService = Depends(get_analytics_service),
) -> DatasetSummary:
    """Return global dataset entity counts."""
    return service.get_dataset_summary()
