import pytest
from unittest.mock import MagicMock
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.exceptions import EntityNotFoundException, DatabaseQueryException
from app.services import (
    RecommendationService,
    get_recommendation_service,
    AnalyticsService,
    get_analytics_service,
)
from app.schemas.services import (
    RecommendationItem,
    RecommendationResult,
    TopRatedMovie,
    GenrePopularity,
    RatingDistributionItem,
    DatasetSummary,
)
from app.schemas.common import MovieRatingStats


@pytest.fixture
def mock_rec_service():
    return MagicMock(spec=RecommendationService)


@pytest.fixture
def mock_analytics_service():
    return MagicMock(spec=AnalyticsService)


# ------------------------------------------------------------------------------
# Recommendation Route Tests
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_similar_movies_route_success(mock_rec_service):
    mock_rec_service.get_similar_movies.return_value = RecommendationResult(
        source_type="movie",
        source_id=1,
        source_title="Toy Story (1995)",
        recommendations=[
            RecommendationItem(
                movie_id=3114,
                title="Toy Story 2 (1999)",
                year=1999,
                genres=["Adventure", "Animation", "Children"],
                score=7.5,
                explanation="Shares 3 genre(s) with 'Toy Story (1995)'",
                imdb_id="0120363",
                tmdb_id="863",
            )
        ],
        total_found=1,
    )

    app.dependency_overrides[get_recommendation_service] = lambda: mock_rec_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/recommendations/movie/1?limit=5")
            assert response.status_code == 200
            data = response.json()
            assert data["source_type"] == "movie"
            assert data["source_id"] == 1
            assert data["source_title"] == "Toy Story (1995)"
            assert len(data["recommendations"]) == 1
            assert data["recommendations"][0]["movie_id"] == 3114
            mock_rec_service.get_similar_movies.assert_called_once_with(movie_id=1, limit=5)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_similar_movies_not_found(mock_rec_service):
    mock_rec_service.get_similar_movies.side_effect = EntityNotFoundException("Movie", 999999)

    app.dependency_overrides[get_recommendation_service] = lambda: mock_rec_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/recommendations/movie/999999")
            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "Not Found"
            assert "999999" in data["message"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_similar_movies_invalid_params():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid movie_id <= 0
        response = await client.get("/api/v1/recommendations/movie/0")
        assert response.status_code == 422

        # Invalid limit > 50
        response2 = await client.get("/api/v1/recommendations/movie/1?limit=100")
        assert response2.status_code == 422


@pytest.mark.asyncio
async def test_get_user_recommendations_route_success(mock_rec_service):
    mock_rec_service.get_user_recommendations.return_value = RecommendationResult(
        source_type="user",
        source_id=42,
        source_title="User #42",
        recommendations=[
            RecommendationItem(
                movie_id=50,
                title="Usual Suspects, The (1995)",
                year=1995,
                genres=["Crime", "Mystery", "Thriller"],
                score=8.2,
                explanation="Recommended based on 10 user(s) with similar rating taste",
            )
        ],
        total_found=1,
    )

    app.dependency_overrides[get_recommendation_service] = lambda: mock_rec_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/recommendations/user/42?limit=10")
            assert response.status_code == 200
            data = response.json()
            assert data["source_type"] == "user"
            assert data["source_id"] == 42
            assert len(data["recommendations"]) == 1
            mock_rec_service.get_user_recommendations.assert_called_once_with(user_id=42, limit=10)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_recommendations_database_failure(mock_rec_service):
    mock_rec_service.get_similar_movies.side_effect = DatabaseQueryException("Neo4j", "Connection reset")

    app.dependency_overrides[get_recommendation_service] = lambda: mock_rec_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/recommendations/movie/1")
            assert response.status_code == 500
            data = response.json()
            assert data["error"] == "Internal Database Error"
            # Ensure no internal query or connection string leaked
            assert "Connection reset" not in data["message"]
    finally:
        app.dependency_overrides.clear()


# ------------------------------------------------------------------------------
# Analytics Route Tests
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_get_top_rated_movies_route(mock_analytics_service):
    mock_analytics_service.get_top_rated_movies.return_value = [
        TopRatedMovie(
            movie_id=318,
            title="Shawshank Redemption, The (1994)",
            release_year=1994,
            avg_rating=4.41,
            rating_count=557,
            genres=["Crime", "Drama"],
        )
    ]

    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/top-rated?min_ratings=20&limit=5")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["movie_id"] == 318
            assert data[0]["avg_rating"] == 4.41
            mock_analytics_service.get_top_rated_movies.assert_called_once_with(min_ratings=20, limit=5)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_top_rated_invalid_params():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid min_ratings <= 0
        response = await client.get("/api/v1/analytics/top-rated?min_ratings=0")
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_genre_popularity_route(mock_analytics_service):
    mock_analytics_service.get_genre_popularity.return_value = [
        GenrePopularity(
            genre="Drama",
            total_ratings=21698,
            distinct_movies=450,
            avg_rating=3.70,
        )
    ]

    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/genres")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["genre"] == "Drama"
            assert data[0]["total_ratings"] == 21698
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_rating_distribution_route(mock_analytics_service):
    mock_analytics_service.get_rating_distribution.return_value = [
        RatingDistributionItem(rating=4.0, count=15000, percentage=30.0)
    ]

    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/ratings/distribution")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["rating"] == 4.0
            assert data[0]["percentage"] == 30.0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_movie_rating_stats_route(mock_analytics_service):
    mock_analytics_service.get_movie_stats.return_value = MovieRatingStats(
        movie_id=1,
        rating_count=215,
        avg_rating=3.92,
    )

    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/movies/1/ratings")
            assert response.status_code == 200
            data = response.json()
            assert data["movie_id"] == 1
            assert data["rating_count"] == 215
            assert data["avg_rating"] == 3.92
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_movie_rating_stats_not_found(mock_analytics_service):
    mock_analytics_service.get_movie_stats.side_effect = EntityNotFoundException("Movie", 999999)

    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/movies/999999/ratings")
            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "Not Found"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_dataset_summary_route(mock_analytics_service):
    mock_analytics_service.get_dataset_summary.return_value = DatasetSummary(
        total_movies=1000,
        total_users=2364,
        total_genres=19,
        total_ratings=50000,
        total_tags=10000,
    )

    app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/analytics/summary")
            assert response.status_code == 200
            data = response.json()
            assert data["total_movies"] == 1000
            assert data["total_users"] == 2364
            assert data["total_ratings"] == 50000
    finally:
        app.dependency_overrides.clear()
