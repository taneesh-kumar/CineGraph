import logging
from contextlib import contextmanager
from typing import Generator, Optional
import pymonetdb
from neo4j import GraphDatabase, Driver, Session
from app.core.config import Settings, get_settings
from app.core.exceptions import DatabaseConnectionException

logger = logging.getLogger("cinegraph-database")


class DatabaseManager:
    """Manages connection lifecycles for Neo4j and MonetDB."""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._neo4j_driver: Optional[Driver] = None

    # --------------------------------------------------------------------------
    # Neo4j Driver Lifecycle & Session Access
    # --------------------------------------------------------------------------
    def get_neo4j_driver(self) -> Driver:
        """Return singleton Neo4j driver, initializing if necessary."""
        if self._neo4j_driver is None:
            try:
                self._neo4j_driver = GraphDatabase.driver(
                    self.settings.NEO4J_URI,
                    auth=(self.settings.NEO4J_USER, self.settings.NEO4J_PASSWORD),
                )
            except Exception as e:
                logger.error(f"Failed to create Neo4j driver: {e}")
                raise DatabaseConnectionException("Neo4j", str(e)) from e
        return self._neo4j_driver

    def close_neo4j_driver(self):
        """Cleanly close the Neo4j driver on application shutdown."""
        if self._neo4j_driver is not None:
            try:
                self._neo4j_driver.close()
                logger.info("Neo4j driver connection closed.")
            except Exception as e:
                logger.warning(f"Error closing Neo4j driver: {e}")
            finally:
                self._neo4j_driver = None

    @contextmanager
    def get_neo4j_session(self) -> Generator[Session, None, None]:
        """Provide a contextual Neo4j session that safely closes after use."""
        driver = self.get_neo4j_driver()
        session = driver.session()
        try:
            yield session
        finally:
            session.close()

    # --------------------------------------------------------------------------
    # MonetDB Connection & Cursor Lifecycle
    # --------------------------------------------------------------------------
    def create_monetdb_connection(self) -> pymonetdb.Connection:
        """Create a new raw connection to MonetDB."""
        try:
            conn = pymonetdb.connect(
                username=self.settings.MONETDB_USER,
                password=self.settings.MONETDB_PASSWORD,
                hostname=self.settings.MONETDB_HOST,
                port=self.settings.MONETDB_PORT,
                database=self.settings.MONETDB_DATABASE,
                autocommit=False,
            )
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to MonetDB: {e}")
            raise DatabaseConnectionException("MonetDB", str(e)) from e

    @contextmanager
    def get_monetdb_connection(self) -> Generator[pymonetdb.Connection, None, None]:
        """
        Provide a managed MonetDB connection that commits on success
        and rolls back / closes safely on error.
        """
        conn = self.create_monetdb_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception as rb_err:
                logger.warning(f"Failed to rollback MonetDB transaction: {rb_err}")
            raise
        finally:
            try:
                conn.close()
            except Exception as cl_err:
                logger.warning(f"Failed to close MonetDB connection: {cl_err}")

    @contextmanager
    def get_monetdb_cursor(self):
        """
        Convenience context manager providing a cursor directly from a managed connection.
        Closes cursor and connection reliably.
        """
        with self.get_monetdb_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                try:
                    cursor.close()
                except Exception as c_err:
                    logger.warning(f"Failed to close MonetDB cursor: {c_err}")

    # --------------------------------------------------------------------------
    # Connectivity / Health Verification
    # --------------------------------------------------------------------------
    def check_neo4j_health(self) -> bool:
        """Check if Neo4j DBMS is reachable and ready."""
        try:
            driver = self.get_neo4j_driver()
            driver.verify_connectivity()
            return True
        except Exception as e:
            logger.warning(f"Neo4j health check failed: {e}")
            return False

    def check_monetdb_health(self) -> bool:
        """Check if MonetDB DBMS is reachable and ready."""
        try:
            with self.get_monetdb_cursor() as cursor:
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                return bool(row and row[0] == 1)
        except Exception as e:
            logger.warning(f"MonetDB health check failed: {e}")
            return False


# Global singleton instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Return singleton DatabaseManager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
