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

    def get_similar_movies_by_genres(
        self,
        movie_id: int,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find candidate movies sharing genres with a given movie.
        Excludes the source movie itself.
        Returns candidate details including shared genre count, all candidate genres,
        and rating count/average if present in graph.
        """
        cypher = """
        MATCH (source:Movie {movieId: $movieId})-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(candidate:Movie)
        WHERE candidate.movieId <> $movieId
        WITH candidate, count(DISTINCT g) AS shared_genre_count, collect(DISTINCT g.name) AS shared_genres
        ORDER BY shared_genre_count DESC, candidate.title ASC
        LIMIT $candidate_pool
        OPTIONAL MATCH (candidate)<-[r:RATED]-()
        WITH candidate, shared_genre_count, shared_genres, count(r) AS rating_count, avg(r.rating) AS avg_rating
        OPTIONAL MATCH (candidate)-[:IN_GENRE]->(cg:Genre)
        RETURN candidate.movieId AS movie_id,
               candidate.title AS title,
               candidate.year AS year,
               candidate.imdbId AS imdb_id,
               candidate.tmdbId AS tmdb_id,
               shared_genre_count,
               shared_genres,
               collect(DISTINCT cg.name) AS all_genres,
               rating_count,
               coalesce(avg_rating, 0.0) AS avg_rating
        ORDER BY shared_genre_count DESC, avg_rating DESC, rating_count DESC, candidate.title ASC
        LIMIT $limit
        """
        try:
            with self.db_manager.get_neo4j_session() as session:
                candidate_pool = max(limit * 5, 50)
                result = session.run(
                    cypher,
                    movieId=movie_id,
                    candidate_pool=candidate_pool,
                    limit=limit,
                )
                candidates = []
                for record in result:
                    candidates.append({
                        "movie_id": record["movie_id"],
                        "title": record["title"],
                        "year": record["year"],
                        "imdb_id": record["imdb_id"],
                        "tmdb_id": record["tmdb_id"],
                        "shared_genre_count": record["shared_genre_count"],
                        "shared_genres": sorted(record["shared_genres"]) if record["shared_genres"] else [],
                        "genres": sorted(record["all_genres"]) if record["all_genres"] else [],
                        "rating_count": record["rating_count"],
                        "avg_rating": round(float(record["avg_rating"]), 2),
                    })
                return candidates
        except Exception as e:
            logger.error(f"Error finding similar movies for movie {movie_id} in Neo4j: {e}")
            raise DatabaseQueryException("Neo4j", str(e)) from e

    def get_collaborative_candidates(
        self,
        user_id: int,
        min_user_rating: float = 3.5,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Collaborative traversal:
        Find candidate movies rated highly by peers who also rated movies highly rated by target user.
        Excludes movies the target user has already rated.
        """
        cypher = """
        MATCH (target:User {userId: $userId})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(peer:User)
        WHERE target <> peer AND r1.rating >= $minRating AND r2.rating >= $minRating
        WITH target, peer, count(DISTINCT m) AS common_liked_count
        WHERE common_liked_count >= 1
        MATCH (peer)-[r3:RATED]->(rec:Movie)
        WHERE r3.rating >= $minRating AND NOT (target)-[:RATED]->(rec)
        OPTIONAL MATCH (rec)-[:IN_GENRE]->(g:Genre)
        WITH rec, count(DISTINCT peer) AS peer_count, avg(r3.rating) AS peer_avg_rating, collect(DISTINCT g.name) AS genres
        RETURN rec.movieId AS movie_id,
               rec.title AS title,
               rec.year AS year,
               rec.imdbId AS imdb_id,
               rec.tmdbId AS tmdb_id,
               peer_count,
               peer_avg_rating,
               genres
        ORDER BY peer_count DESC, peer_avg_rating DESC, rec.title ASC
        LIMIT $limit
        """
        try:
            with self.db_manager.get_neo4j_session() as session:
                result = session.run(
                    cypher,
                    userId=user_id,
                    minRating=min_user_rating,
                    limit=limit,
                )
                candidates = []
                for record in result:
                    candidates.append({
                        "movie_id": record["movie_id"],
                        "title": record["title"],
                        "year": record["year"],
                        "imdb_id": record["imdb_id"],
                        "tmdb_id": record["tmdb_id"],
                        "peer_count": record["peer_count"],
                        "peer_avg_rating": round(float(record["peer_avg_rating"]), 2),
                        "genres": sorted(record["genres"]) if record["genres"] else [],
                    })
                return candidates
        except Exception as e:
            logger.error(f"Error fetching collaborative candidates for user {user_id} in Neo4j: {e}")
            raise DatabaseQueryException("Neo4j", str(e)) from e

