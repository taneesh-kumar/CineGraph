import pytest
from unittest.mock import MagicMock
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.database import DatabaseManager, get_db_manager


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify that the GET /health endpoint returns HTTP 200 and healthy status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "CineGraph API"
        assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint_v1():
    """Verify that the versioned GET /api/v1/health endpoint behaves identically."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "CineGraph API"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify that the root endpoint identifies the service as CineGraph API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "CineGraph API"
        assert data["status"] == "online"
        assert "api_v1_prefix" in data


@pytest.mark.asyncio
async def test_ready_endpoint_both_healthy():
    """Verify /ready returns 200 when both Neo4j and MonetDB are reachable."""
    mock_db_manager = MagicMock(spec=DatabaseManager)
    mock_db_manager.check_neo4j_health.return_value = True
    mock_db_manager.check_monetdb_health.return_value = True

    app.dependency_overrides[get_db_manager] = lambda: mock_db_manager
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["neo4j"]["status"] == "connected"
            assert data["monetdb"]["status"] == "connected"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_ready_endpoint_database_unavailable():
    """Verify /ready returns 503 when MonetDB or Neo4j is unreachable without leaking credentials."""
    mock_db_manager = MagicMock(spec=DatabaseManager)
    mock_db_manager.check_neo4j_health.return_value = True
    mock_db_manager.check_monetdb_health.return_value = False

    app.dependency_overrides[get_db_manager] = lambda: mock_db_manager
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/ready")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unavailable"
            assert data["neo4j"]["status"] == "connected"
            assert data["monetdb"]["status"] == "unavailable"
            # Ensure no credentials or trace leaked
            assert "password" not in response.text.lower()
            assert "traceback" not in response.text.lower()
    finally:
        app.dependency_overrides.clear()
