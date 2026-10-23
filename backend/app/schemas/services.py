from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import (
    GenreModel,
    MovieLinksModel,
    MovieSummary,
    UserRating,
    MovieRatingStats,
    HealthResponse,
    DatabaseStatus,
    ReadinessResponse,
)


class RecommendationItem(BaseModel):
    movie_id: int
    title: str
    year: Optional[int] = None
    genres: List[str] = Field(default_factory=list)
    score: float = Field(..., description="Calculated recommendation score")
    explanation: str = Field(..., description="Transparent textual explanation for recommendation")
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None


class RecommendationResult(BaseModel):
    source_type: str = Field(..., description="'movie' or 'user'")
    source_id: int
    source_title: Optional[str] = None
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    total_found: int = 0


class TopRatedMovie(BaseModel):
    movie_id: int
    title: str
    release_year: Optional[int] = None
    avg_rating: float
    rating_count: int
    genres: List[str] = Field(default_factory=list)


class GenrePopularity(BaseModel):
    genre: str
    total_ratings: int = Field(..., description="Total count of rating events in this genre")
    distinct_movies: int = Field(..., description="Number of rated movies in this genre")
    avg_rating: float = Field(..., description="Average rating value for movies in this genre")


class RatingDistributionItem(BaseModel):
    rating: float = Field(..., description="Rating score (0.5 to 5.0 in increments of 0.5)")
    count: int = Field(..., description="Total number of ratings with this score")
    percentage: float = Field(..., description="Percentage of total ratings")


class DatasetSummary(BaseModel):
    total_movies: int
    total_users: int
    total_genres: int
    total_ratings: int
    total_tags: int
