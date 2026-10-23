from app.repositories.neo4j_repo import Neo4jRepository
from app.repositories.monetdb_repo import MonetDBRepository
from app.core.database import get_db_manager


def get_neo4j_repo() -> Neo4jRepository:
    """FastAPI dependency for accessing Neo4jRepository."""
    return Neo4jRepository(db_manager=get_db_manager())


def get_monetdb_repo() -> MonetDBRepository:
    """FastAPI dependency for accessing MonetDBRepository."""
    return MonetDBRepository(db_manager=get_db_manager())


__all__ = [
    "Neo4jRepository",
    "MonetDBRepository",
    "get_neo4j_repo",
    "get_monetdb_repo",
]
