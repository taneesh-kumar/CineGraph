import pytest
from unittest.mock import MagicMock
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.repositories import Neo4jRepository, get_neo4j_repo


@pytest.fixture
def mock_neo4j_repo():
    return MagicMock(spec=Neo4jRepository)


@pytest.mark.asyncio
async def test_search_movies_route_success(mock_neo4j_repo):
    mock_neo4j_repo.search_movies_by_title.return_value = [
        {
            "movie_id": 1,
            "title": "Toy Story (1995)",
            "year": 1995,
            "imdb_id": "0114709",
            "tmdb_id": "862",
            "genres": ["Adventure", "Animation", "Children"],
        }
    ]

    app.dependency_overrides[get_neo4j_repo] = lambda: mock_neo4j_repo
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/movies/search?q=Toy&limit=10")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["movie_id"] == 1
            assert data[0]["title"] == "Toy Story (1995)"
            assert data[0]["genres"] == ["Adventure", "Animation", "Children"]
            mock_neo4j_repo.search_movies_by_title.assert_called_once_with(query_str="Toy", limit=10)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_movie_route_success(mock_neo4j_repo):
    mock_neo4j_repo.get_movie_by_id.return_value = {
        "movie_id": 1,
        "title": "Toy Story (1995)",
        "year": 1995,
        "imdb_id": "0114709",
        "tmdb_id": "862",
        "genres": ["Adventure", "Animation", "Children"],
    }

    app.dependency_overrides[get_neo4j_repo] = lambda: mock_neo4j_repo
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/movies/1")
            assert response.status_code == 200
            data = response.json()
            assert data["movie_id"] == 1
            assert data["title"] == "Toy Story (1995)"
            mock_neo4j_repo.get_movie_by_id.assert_called_once_with(1)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_movie_not_found(mock_neo4j_repo):
    mock_neo4j_repo.get_movie_by_id.return_value = None

    app.dependency_overrides[get_neo4j_repo] = lambda: mock_neo4j_repo
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/movies/999999")
            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "Not Found"
            assert "999999" in data["message"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_movie_invalid_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/movies/0")
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_movies_route(mock_neo4j_repo):
    mock_neo4j_repo.search_movies_by_title.return_value = [
        {
            "movie_id": 1,
            "title": "Toy Story (1995)",
            "year": 1995,
            "imdb_id": "0114709",
            "tmdb_id": "862",
            "genres": ["Animation"],
        }
    ]

    app.dependency_overrides[get_neo4j_repo] = lambda: mock_neo4j_repo
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/movies?limit=5")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            mock_neo4j_repo.search_movies_by_title.assert_called_once_with(query_str="", limit=5)
    finally:
        app.dependency_overrides.clear()
