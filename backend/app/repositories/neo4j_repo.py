import logging
from typing import Any, Dict, List, Optional
from app.core.database import DatabaseManager, get_db_manager
from app.core.exceptions import DatabaseQueryException

logger = logging.getLogger("cinegraph-neo4j-repo")


class Neo4jRepository:
    """
    Data-access repository for Neo4j graph operations.
    Encapsulates Cypher queries using parameterized execution.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or get_db_manager()

    def get_movie_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        1. Fetch a movie by its MovieLens ID, including connected genres.
        Returns normalized dictionary or None if not found.
        """
        query = """
        MATCH (m:Movie {movieId: $movieId})
        OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
        RETURN m.movieId AS movie_id,
               m.title AS title,
               m.year AS year,
               m.imdbId AS imdb_id,
               m.tmdbId AS tmdb_id,
               collect(DISTINCT g.name) AS genres
        """
        try:
            with self.db_manager.get_neo4j_session() as session:
                result = session.run(query, movieId=movie_id)
                record = result.single()
                if not record or record["movie_id"] is None:
                    return None
                return {
                    "movie_id": record["movie_id"],
                    "title": record["title"],
                    "year": record["year"],
                    "imdb_id": record["imdb_id"],
                    "tmdb_id": record["tmdb_id"],
                    "genres": sorted(record["genres"]) if record["genres"] else [],
                }
        except Exception as e:
            logger.error(f"Error fetching movie {movie_id} from Neo4j: {e}")
            raise DatabaseQueryException("Neo4j", str(e)) from e

    def search_movies_by_title(self, query_str: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        2. Search movies by title (case-insensitive substring match).
        Uses parameterized query with deterministic ordering.
        """
        cypher = """
        MATCH (m:Movie)
        WHERE toLower(m.title) CONTAINS toLower($title_query)
        OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
        RETURN m.movieId AS movie_id,
               m.title AS title,
               m.year AS year,
               m.imdbId AS imdb_id,
               m.tmdbId AS tmdb_id,
               collect(DISTINCT g.name) AS genres
        ORDER BY m.year DESC, m.title ASC
        LIMIT $limit
        """
        try:
            with self.db_manager.get_neo4j_session() as session:
                result = session.run(cypher, title_query=query_str, limit=limit)
                movies = []
                for record in result:
                    movies.append({
                        "movie_id": record["movie_id"],
                        "title": record["title"],
                        "year": record["year"],
                        "imdb_id": record["imdb_id"],
                        "tmdb_id": record["tmdb_id"],
                        "genres": sorted(record["genres"]) if record["genres"] else [],
                    })
                return movies
        except Exception as e:
            logger.error(f"Error searching movies with query '{query_str}' in Neo4j: {e}")
            raise DatabaseQueryException("Neo4j", str(e)) from e

    def get_genres_for_movie(self, movie_id: int) -> List[str]:
        """
        3. Fetch genres associated with a specific movie.
        """
        query = """
        MATCH (m:Movie {movieId: $movieId})-[:IN_GENRE]->(g:Genre)
        RETURN g.name AS genre_name
        ORDER BY g.name ASC
        """
        try:
            with self.db_manager.get_neo4j_session() as session:
                result = session.run(query, movieId=movie_id)
                return [record["genre_name"] for record in result]
        except Exception as e:
            logger.error(f"Error fetching genres for movie {movie_id} from Neo4j: {e}")
            raise DatabaseQueryException("Neo4j", str(e)) from e

    def get_user_ratings(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        4. Fetch a user's rated movies and ratings.
        """
        query = """
        MATCH (u:User {userId: $userId})-[r:RATED]->(m:Movie)
        RETURN u.userId AS user_id,
               m.movieId AS movie_id,
               m.title AS movie_title,
               r.rating AS rating,
               r.timestamp AS timestamp
        ORDER BY r.timestamp DESC, m.movieId ASC
        LIMIT $limit
        """
        try:
            with self.db_manager.get_neo4j_session() as session:
                result = session.run(query, userId=user_id, limit=limit)
                ratings = []
                for record in result:
                    ratings.append({
                        "user_id": record["user_id"],
                        "movie_id": record["movie_id"],
                        "movie_title": record["movie_title"],
                        "rating": float(record["rating"]) if record["rating"] is not None else 0.0,
                        "timestamp": record["timestamp"],
                    })
                return ratings
        except Exception as e:
            logger.error(f"Error fetching ratings for user {user_id} from Neo4j: {e}")
            raise DatabaseQueryException("Neo4j", str(e)) from e

    def get_users_who_rated_movie(self, movie_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        5. Fetch users who rated a specified movie.
        """
        query = """
        MATCH (u:User)-[r:RATED]->(m:Movie {movieId: $movieId})
        RETURN u.userId AS user_id,
               m.movieId AS movie_id,
               r.rating AS rating,
               r.timestamp AS timestamp
        ORDER BY r.timestamp DESC, u.userId ASC
        LIMIT $limit
        """
        try:
            with self.db_manager.get_neo4j_session() as session:
                result = session.run(query, movieId=movie_id, limit=limit)
                users = []
                for record in result:
                    users.append({
                        "user_id": record["user_id"],
                        "movie_id": record["movie_id"],
                        "rating": float(record["rating"]) if record["rating"] is not None else 0.0,
                        "timestamp": record["timestamp"],
                    })
                return users
        except Exception as e:
            logger.error(f"Error fetching users who rated movie {movie_id} from Neo4j: {e}")
            raise DatabaseQueryException("Neo4j", str(e)) from e

    def get_movies_rated_by_user(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        6. Fetch movies rated by a specified user, returning movie node info and user rating.
        """
        query = """
        MATCH (u:User {userId: $userId})-[r:RATED]->(m:Movie)
        OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
        RETURN m.movieId AS movie_id,
               m.title AS title,
               m.year AS year,
               m.imdbId AS imdb_id,
               m.tmdbId AS tmdb_id,
               r.rating AS user_rating,
               r.timestamp AS rated_timestamp,
               collect(DISTINCT g.name) AS genres
        ORDER BY r.timestamp DESC, m.movieId ASC
        LIMIT $limit
        """
        try:
            with self.db_manager.get_neo4j_session() as session:
                result = session.run(query, userId=user_id, limit=limit)
                movies = []
                for record in result:
                    movies.append({
                        "movie_id": record["movie_id"],
                        "title": record["title"],
                        "year": record["year"],
                        "imdb_id": record["imdb_id"],
                        "tmdb_id": record["tmdb_id"],
                        "user_rating": float(record["user_rating"]) if record["user_rating"] is not None else 0.0,
                        "rated_timestamp": record["rated_timestamp"],
                        "genres": sorted(record["genres"]) if record["genres"] else [],
                    })
                return movies
        except Exception as e:
            logger.error(f"Error fetching movies rated by user {user_id} from Neo4j: {e}")
            raise DatabaseQueryException("Neo4j", str(e)) from e
