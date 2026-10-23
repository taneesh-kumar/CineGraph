import logging
from typing import Any, Dict, List, Optional
from app.core.database import DatabaseManager, get_db_manager
from app.core.exceptions import DatabaseQueryException

logger = logging.getLogger("cinegraph-monetdb-repo")


class MonetDBRepository:
    """
    Data-access repository for MonetDB analytical database operations.
    Encapsulates SQL queries using parameterized execution and safe cursor lifecycles.
    Respects the existing schema (e.g., 'movie_users' instead of 'users').
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager or get_db_manager()

    def get_movie_by_id(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        1. Fetch a movie by its ID, including external links (imdbId, tmdbId) and genres.
        """
        sql_movie = """
        SELECT m.movie_id, m.title, m.release_year, l.imdb_id, l.tmdb_id
        FROM movies m
        LEFT JOIN movie_links l ON m.movie_id = l.movie_id
        WHERE m.movie_id = %s;
        """
        sql_genres = """
        SELECT g.name
        FROM movie_genres mg
        JOIN genres g ON mg.genre_id = g.genre_id
        WHERE mg.movie_id = %s
        ORDER BY g.name ASC;
        """
        try:
            with self.db_manager.get_monetdb_cursor() as cursor:
                cursor.execute(sql_movie, (movie_id,))
                row = cursor.fetchone()
                if not row:
                    return None

                cursor.execute(sql_genres, (movie_id,))
                genre_rows = cursor.fetchall()
                genres = [g[0] for g in genre_rows]

                return {
                    "movie_id": row[0],
                    "title": row[1],
                    "year": row[2],
                    "imdb_id": row[3],
                    "tmdb_id": row[4],
                    "genres": genres,
                }
        except Exception as e:
            logger.error(f"Error fetching movie {movie_id} from MonetDB: {e}")
            raise DatabaseQueryException("MonetDB", str(e)) from e

    def search_movies_by_title(self, query_str: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        2. Search movies by title (case-insensitive substring match).
        """
        sql = """
        SELECT m.movie_id, m.title, m.release_year, l.imdb_id, l.tmdb_id
        FROM movies m
        LEFT JOIN movie_links l ON m.movie_id = l.movie_id
        WHERE LOWER(m.title) LIKE LOWER(%s)
        ORDER BY m.release_year DESC, m.title ASC
        LIMIT %s;
        """
        try:
            with self.db_manager.get_monetdb_cursor() as cursor:
                param = f"%{query_str}%"
                cursor.execute(sql, (param, limit))
                rows = cursor.fetchall()

                movies = []
                for row in rows:
                    movies.append({
                        "movie_id": row[0],
                        "title": row[1],
                        "year": row[2],
                        "imdb_id": row[3],
                        "tmdb_id": row[4],
                    })
                return movies
        except Exception as e:
            logger.error(f"Error searching movies with query '{query_str}' in MonetDB: {e}")
            raise DatabaseQueryException("MonetDB", str(e)) from e

    def get_genres_for_movie(self, movie_id: int) -> List[str]:
        """
        3. Fetch genres associated with a specific movie.
        """
        sql = """
        SELECT g.name
        FROM movie_genres mg
        JOIN genres g ON mg.genre_id = g.genre_id
        WHERE mg.movie_id = %s
        ORDER BY g.name ASC;
        """
        try:
            with self.db_manager.get_monetdb_cursor() as cursor:
                cursor.execute(sql, (movie_id,))
                rows = cursor.fetchall()
                return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"Error fetching genres for movie {movie_id} from MonetDB: {e}")
            raise DatabaseQueryException("MonetDB", str(e)) from e

    def get_ratings_for_movie(self, movie_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        4. Fetch ratings for a movie.
        """
        sql = """
        SELECT r.user_id, r.movie_id, r.rating, r.rated_at
        FROM ratings r
        WHERE r.movie_id = %s
        ORDER BY r.rated_at DESC, r.user_id ASC
        LIMIT %s;
        """
        try:
            with self.db_manager.get_monetdb_cursor() as cursor:
                cursor.execute(sql, (movie_id, limit))
                rows = cursor.fetchall()
                ratings = []
                for row in rows:
                    ratings.append({
                        "user_id": row[0],
                        "movie_id": row[1],
                        "rating": float(row[2]) if row[2] is not None else 0.0,
                        "rated_at": row[3].isoformat() if hasattr(row[3], "isoformat") else str(row[3]),
                    })
                return ratings
        except Exception as e:
            logger.error(f"Error fetching ratings for movie {movie_id} from MonetDB: {e}")
            raise DatabaseQueryException("MonetDB", str(e)) from e

    def get_ratings_by_user(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        5. Fetch ratings given by a user, joining with movie titles.
        Uses movie_users table reference.
        """
        sql = """
        SELECT r.user_id, r.movie_id, m.title, r.rating, r.rated_at
        FROM ratings r
        JOIN movies m ON r.movie_id = m.movie_id
        WHERE r.user_id = %s
        ORDER BY r.rated_at DESC, r.movie_id ASC
        LIMIT %s;
        """
        try:
            with self.db_manager.get_monetdb_cursor() as cursor:
                cursor.execute(sql, (user_id, limit))
                rows = cursor.fetchall()
                ratings = []
                for row in rows:
                    ratings.append({
                        "user_id": row[0],
                        "movie_id": row[1],
                        "movie_title": row[2],
                        "rating": float(row[3]) if row[3] is not None else 0.0,
                        "rated_at": row[4].isoformat() if hasattr(row[4], "isoformat") else str(row[4]),
                    })
                return ratings
        except Exception as e:
            logger.error(f"Error fetching ratings for user {user_id} from MonetDB: {e}")
            raise DatabaseQueryException("MonetDB", str(e)) from e

    def get_movie_rating_stats(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        6. Fetch rating count and average rating for a movie.
        """
        sql = """
        SELECT COUNT(rating) AS rating_count, AVG(rating) AS avg_rating
        FROM ratings
        WHERE movie_id = %s;
        """
        try:
            with self.db_manager.get_monetdb_cursor() as cursor:
                cursor.execute(sql, (movie_id,))
                row = cursor.fetchone()
                if not row or row[0] == 0:
                    return {
                        "movie_id": movie_id,
                        "rating_count": 0,
                        "avg_rating": 0.0,
                    }
                return {
                    "movie_id": movie_id,
                    "rating_count": int(row[0]),
                    "avg_rating": round(float(row[1]), 2) if row[1] is not None else 0.0,
                }
        except Exception as e:
            logger.error(f"Error calculating rating stats for movie {movie_id} in MonetDB: {e}")
            raise DatabaseQueryException("MonetDB", str(e)) from e
