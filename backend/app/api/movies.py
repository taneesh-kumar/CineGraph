import logging
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Path, Query
from app.repositories import Neo4jRepository, get_neo4j_repo
from app.schemas.common import MovieSummary
from app.core.exceptions import EntityNotFoundException

logger = logging.getLogger("cinegraph-movies-api")

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get(
    "/search",
    response_model=List[MovieSummary],
    summary="Search movies by title",
    description="Search for movies matching a case-insensitive title substring.",
)
async def search_movies(
    q: Annotated[str, Query(description="Title search substring")] = "",
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of movies to return")
    ] = 20,
    repo: Neo4jRepository = Depends(get_neo4j_repo),
) -> List[MovieSummary]:
    """Search movies by title with a bounded result limit."""
    results = repo.search_movies_by_title(query_str=q, limit=limit)
    return [MovieSummary(**item) for item in results]


@router.get(
    "/{movie_id}",
    response_model=MovieSummary,
    summary="Get movie details by ID",
    description="Fetches movie details including release year, external IDs, and connected genres.",
)
async def get_movie(
    movie_id: Annotated[int, Path(ge=1, description="MovieLens movie ID")],
    repo: Neo4jRepository = Depends(get_neo4j_repo),
) -> MovieSummary:
    """Fetch movie metadata and genres by movie ID."""
    movie = repo.get_movie_by_id(movie_id)
    if not movie:
        raise EntityNotFoundException("Movie", movie_id)
    return MovieSummary(**movie)


@router.get(
    "",
    response_model=List[MovieSummary],
    summary="List movies",
    description="Returns a list of movies from the dataset, ordered by year descending.",
)
async def list_movies(
    limit: Annotated[
        int, Query(ge=1, le=100, description="Maximum number of movies to return")
    ] = 20,
    repo: Neo4jRepository = Depends(get_neo4j_repo),
) -> List[MovieSummary]:
    """List sample movies ordered by year descending."""
    results = repo.search_movies_by_title(query_str="", limit=limit)
    return [MovieSummary(**item) for item in results]
