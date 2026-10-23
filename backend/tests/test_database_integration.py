import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import get_db_manager
from app.repositories.neo4j_repo import Neo4jRepository
from app.repositories.monetdb_repo import MonetDBRepository


@pytest.mark.asyncio
async def test_live_readiness_probe():
    """Verify live readiness probe against the actual running Docker database containers."""
    db_manager = get_db_manager()
    if not (db_manager.check_neo4j_health() and db_manager.check_monetdb_health()):
        pytest.skip("Docker database containers are not running.")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["neo4j"]["status"] == "connected"
        assert data["monetdb"]["status"] == "connected"


def test_live_neo4j_repository_queries():
    """Verify live queries execute on actual Neo4j container without error."""
    db_manager = get_db_manager()
    if not db_manager.check_neo4j_health():
        pytest.skip("Neo4j database container is not running.")

    repo = Neo4jRepository(db_manager=db_manager)
    # Test movie fetch
    movie = repo.get_movie_by_id(1)
    assert movie is not None
    assert movie["movie_id"] == 1
    assert "Toy Story" in movie["title"]
    assert len(movie["genres"]) > 0

    # Test title search
    search_res = repo.search_movies_by_title("Jumanji", limit=5)
    assert len(search_res) >= 1
    assert any(m["movie_id"] == 2 for m in search_res)

    # Test genres
    genres = repo.get_genres_for_movie(1)
    assert len(genres) > 0

    # Test users who rated
    users = repo.get_users_who_rated_movie(1, limit=5)
    assert len(users) > 0


def test_live_monetdb_repository_queries():
    """Verify live queries execute on actual MonetDB container without error."""
    db_manager = get_db_manager()
    if not db_manager.check_monetdb_health():
        pytest.skip("MonetDB database container is not running.")

    repo = MonetDBRepository(db_manager=db_manager)
    # Test movie fetch
    movie = repo.get_movie_by_id(1)
    assert movie is not None
    assert movie["movie_id"] == 1
    assert "Toy Story" in movie["title"]

    # Test search
    search_res = repo.search_movies_by_title("Toy", limit=5)
    assert len(search_res) >= 1

    # Test stats
    stats = repo.get_movie_rating_stats(1)
    assert stats is not None
    assert stats["movie_id"] == 1
    assert stats["rating_count"] > 0
    assert stats["avg_rating"] > 0.0
