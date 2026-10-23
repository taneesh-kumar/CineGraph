from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class GenreModel(BaseModel):
    name: str
    genre_id: Optional[int] = None


class MovieLinksModel(BaseModel):
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None


class MovieSummary(BaseModel):
    movie_id: int
    title: str
    year: Optional[int] = None
    genres: List[str] = Field(default_factory=list)
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None


class UserRating(BaseModel):
    user_id: int
    movie_id: int
    rating: float
    rated_at: Optional[datetime] = None
    timestamp: Optional[int] = None
    movie_title: Optional[str] = None


class MovieRatingStats(BaseModel):
    movie_id: int
    rating_count: int
    avg_rating: float


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class DatabaseStatus(BaseModel):
    status: str
    details: Optional[str] = None


class ReadinessResponse(BaseModel):
    status: str
    neo4j: DatabaseStatus
    monetdb: DatabaseStatus
