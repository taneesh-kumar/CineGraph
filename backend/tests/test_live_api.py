import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import get_db_manager


@pytest.mark.asyncio
async def test_live_recommendation_and_analytics_routes():
    """Verify live API responses from actual database containers."""
    db_manager = get_db_manager()
    if not (db_manager.check_neo4j_health() and db_manager.check_monetdb_health()):
        pytest.skip("Docker database containers are not running.")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Movie Recommendations for Tenet (217465)
        res_movie_rec = await client.get("/api/v1/recommendations/movie/217465?limit=3")
        assert res_movie_rec.status_code == 200
        data_movie = res_movie_rec.json()
        assert data_movie["source_id"] == 217465
        assert len(data_movie["recommendations"]) > 0
        assert data_movie["recommendations"][0]["movie_id"] != 217465
        assert "explanation" in data_movie["recommendations"][0]

        # 2. User Recommendations for User 57304
        res_user_rec = await client.get("/api/v1/recommendations/user/57304?limit=3")
        assert res_user_rec.status_code == 200
        data_user = res_user_rec.json()
        assert data_user["source_id"] == 57304

        # 3. Top Rated Movies
        res_top = await client.get("/api/v1/analytics/top-rated?min_ratings=20&limit=3")
        assert res_top.status_code == 200
        data_top = res_top.json()
        assert len(data_top) == 3
        assert data_top[0]["rating_count"] >= 20

        # 4. Genre Popularity
        res_genres = await client.get("/api/v1/analytics/genres")
        assert res_genres.status_code == 200
        data_genres = res_genres.json()
        assert len(data_genres) > 0
        assert data_genres[0]["total_ratings"] > 0

        # 5. Rating Distribution
        res_dist = await client.get("/api/v1/analytics/ratings/distribution")
        assert res_dist.status_code == 200
        data_dist = res_dist.json()
        assert len(data_dist) == 10  # 0.5 to 5.0 in 0.5 increments
        total_pct = sum(d["percentage"] for d in data_dist)
        assert 99.0 <= total_pct <= 101.0

        # 6. Movie Ratings for Tenet (217465)
        res_movie_stats = await client.get("/api/v1/analytics/movies/217465/ratings")
        assert res_movie_stats.status_code == 200
        data_stats = res_movie_stats.json()
        assert data_stats["movie_id"] == 217465
        assert data_stats["rating_count"] > 0
        assert data_stats["avg_rating"] > 0.0

        # 7. Dataset Summary
        res_summary = await client.get("/api/v1/analytics/summary")
        assert res_summary.status_code == 200
        data_summary = res_summary.json()
        assert data_summary["total_movies"] == 2500
        assert data_summary["total_users"] >= 16000
        assert data_summary["total_genres"] == 16
        assert data_summary["total_ratings"] == 119689
        assert data_summary["total_tags"] >= 25000
