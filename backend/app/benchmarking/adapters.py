"""Benchmark database adapters for Neo4j and MonetDB direct query execution."""
import time
from typing import Any, Callable, Dict, List, Tuple
from app.core.database import DatabaseManager
from app.repositories import Neo4jRepository, MonetDBRepository


class Neo4jBenchmarkAdapter:
    """Adapter executing direct Cypher queries via pooled Neo4j driver session."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.repo = Neo4jRepository(db_manager=db_manager)

    def execute_timed(self, func: Callable, *args, **kwargs) -> Tuple[float, Any]:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = (time.perf_counter() - start) * 1000.0
        return duration_ms, result

    # Workload A: Entity Lookup
    def get_movie_by_id(self, movie_id: int):
        return self.execute_timed(self.repo.get_movie_by_id, movie_id)

    # Workload B: Title Search
    def search_movies(self, query_str: str, limit: int = 20):
        return self.execute_timed(self.repo.search_movies_by_title, query_str, limit)

    # Workload C: Genre Relationships
    def get_genres_for_movie(self, movie_id: int):
        return self.execute_timed(self.repo.get_genres_for_movie, movie_id)

    # Workload D: Graph Traversals
    def get_users_who_rated(self, movie_id: int, limit: int = 50):
        return self.execute_timed(self.repo.get_users_who_rated_movie, movie_id, limit)

    def get_movies_rated_by_user(self, user_id: int, limit: int = 50):
        return self.execute_timed(self.repo.get_movies_rated_by_user, user_id, limit)

    def get_similar_candidates(self, movie_id: int, limit: int = 10):
        return self.execute_timed(self.repo.get_similar_movies_by_genres, movie_id, limit)

    def get_collaborative_candidates(self, user_id: int, limit: int = 10):
        return self.execute_timed(self.repo.get_collaborative_candidates, user_id, 3.5, limit)


class MonetDBBenchmarkAdapter:
    """Adapter executing columnar SQL queries via MonetDB cursor connection."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.repo = MonetDBRepository(db_manager=db_manager)

    def execute_timed(self, func: Callable, *args, **kwargs) -> Tuple[float, Any]:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration_ms = (time.perf_counter() - start) * 1000.0
        return duration_ms, result

    # Workload A: Entity Lookup
    def get_movie_by_id(self, movie_id: int):
        return self.execute_timed(self.repo.get_movie_by_id, movie_id)

    # Workload B: Title Search
    def search_movies(self, query_str: str, limit: int = 20):
        return self.execute_timed(self.repo.search_movies_by_title, query_str, limit)

    # Workload C: Genre Relationships
    def get_genres_for_movie(self, movie_id: int):
        return self.execute_timed(self.repo.get_genres_for_movie, movie_id)

    # Workload E: Analytical Aggregations
    def get_movie_rating_stats(self, movie_id: int):
        return self.execute_timed(self.repo.get_movie_rating_stats, movie_id)

    def get_top_rated_movies(self, min_ratings: int = 20, limit: int = 20):
        return self.execute_timed(self.repo.get_top_rated_movies, min_ratings, limit)

    def get_genre_popularity(self):
        return self.execute_timed(self.repo.get_genre_popularity)

    def get_rating_distribution(self):
        return self.execute_timed(self.repo.get_rating_distribution)

    def get_dataset_summary(self):
        return self.execute_timed(self.repo.get_dataset_counts)
