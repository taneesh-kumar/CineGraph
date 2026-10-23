"""Benchmark workload definitions and execution runners."""
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from app.benchmarking.models import (
    RawMeasurement,
    TargetEngine,
    ExecutionMode,
    BenchmarkConfig,
    CorrectnessComparison,
)
from app.benchmarking.adapters import Neo4jBenchmarkAdapter, MonetDBBenchmarkAdapter


class WorkloadDefinition:
    """Represents a discrete benchmark workload with configurable inputs."""

    def __init__(
        self,
        workload_id: str,
        operation: str,
        target_engine: TargetEngine,
        execution_mode: ExecutionMode,
        func: Callable[[], Tuple[float, Any]],
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.workload_id = workload_id
        self.operation = operation
        self.target_engine = target_engine
        self.execution_mode = execution_mode
        self.func = func
        self.parameters = parameters or {}


def build_workloads(
    neo4j_adapter: Neo4jBenchmarkAdapter,
    monetdb_adapter: MonetDBBenchmarkAdapter,
    sample_movie_ids: List[int],
    sample_user_ids: List[int],
) -> List[WorkloadDefinition]:
    """
    Construct comparable and database-native workloads across Workloads A-E.
    """
    workloads: List[WorkloadDefinition] = []
    primary_movie_id = sample_movie_ids[0] if sample_movie_ids else 217465  # Tenet
    primary_user_id = sample_user_ids[0] if sample_user_ids else 57304

    # --------------------------------------------------------------------------
    # Workload A: Entity Lookup (Cross-Database Comparable)
    # --------------------------------------------------------------------------
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_a_lookup_neo4j",
            operation="lookup_movie_by_id",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: neo4j_adapter.get_movie_by_id(primary_movie_id),
            parameters={"movie_id": primary_movie_id},
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_a_lookup_monetdb",
            operation="lookup_movie_by_id",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: monetdb_adapter.get_movie_by_id(primary_movie_id),
            parameters={"movie_id": primary_movie_id},
        )
    )

    # --------------------------------------------------------------------------
    # Workload B: Title Search (Cross-Database Comparable)
    # Broad ("Soul"), Selective ("Tenet"), No-match ("NonExistentXYZ")
    # --------------------------------------------------------------------------
    for query_term, label in [("Soul", "broad"), ("Tenet", "selective"), ("NonExistentXYZ", "nomatch")]:
        workloads.append(
            WorkloadDefinition(
                workload_id=f"workload_b_search_neo4j_{label}",
                operation=f"search_movies_{label}",
                target_engine=TargetEngine.NEO4J,
                execution_mode=ExecutionMode.DATABASE_QUERY,
                func=(lambda q=query_term: neo4j_adapter.search_movies(q, limit=20)),
                parameters={"query": query_term, "limit": 20},
            )
        )
        workloads.append(
            WorkloadDefinition(
                workload_id=f"workload_b_search_monetdb_{label}",
                operation=f"search_movies_{label}",
                target_engine=TargetEngine.MONETDB,
                execution_mode=ExecutionMode.DATABASE_QUERY,
                func=(lambda q=query_term: monetdb_adapter.search_movies(q, limit=20)),
                parameters={"query": query_term, "limit": 20},
            )
        )

    # --------------------------------------------------------------------------
    # Workload C: Genre Relationships (Cross-Database Comparable)
    # --------------------------------------------------------------------------
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_c_genres_neo4j",
            operation="get_movie_genres",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: neo4j_adapter.get_genres_for_movie(primary_movie_id),
            parameters={"movie_id": primary_movie_id},
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_c_genres_monetdb",
            operation="get_movie_genres",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: monetdb_adapter.get_genres_for_movie(primary_movie_id),
            parameters={"movie_id": primary_movie_id},
        )
    )

    # --------------------------------------------------------------------------
    # Workload D: Graph Traversals (Neo4j Native)
    # --------------------------------------------------------------------------
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_d_users_rated_neo4j",
            operation="traverse_users_who_rated",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: neo4j_adapter.get_users_who_rated(primary_movie_id, limit=50),
            parameters={"movie_id": primary_movie_id, "limit": 50},
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_d_movies_rated_neo4j",
            operation="traverse_movies_rated_by_user",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: neo4j_adapter.get_movies_rated_by_user(primary_user_id, limit=50),
            parameters={"user_id": primary_user_id, "limit": 50},
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_d_similar_candidates_neo4j",
            operation="traverse_similar_movie_candidates",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: neo4j_adapter.get_similar_candidates(primary_movie_id, limit=10),
            parameters={"movie_id": primary_movie_id, "limit": 10},
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_d_collaborative_traversal_neo4j",
            operation="traverse_collaborative_peer_candidates",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: neo4j_adapter.get_collaborative_candidates(primary_user_id, limit=10),
            parameters={"user_id": primary_user_id, "limit": 10},
        )
    )

    # --------------------------------------------------------------------------
    # Workload E: Analytical Aggregations (MonetDB Native)
    # --------------------------------------------------------------------------
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_e_rating_stats_monetdb",
            operation="aggregate_movie_rating_stats",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: monetdb_adapter.get_movie_rating_stats(primary_movie_id),
            parameters={"movie_id": primary_movie_id},
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_e_top_rated_monetdb",
            operation="aggregate_top_rated_movies",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: monetdb_adapter.get_top_rated_movies(min_ratings=20, limit=20),
            parameters={"min_ratings": 20, "limit": 20},
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_e_genre_popularity_monetdb",
            operation="aggregate_genre_popularity",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: monetdb_adapter.get_genre_popularity(),
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_e_rating_distribution_monetdb",
            operation="aggregate_rating_distribution",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: monetdb_adapter.get_rating_distribution(),
        )
    )
    workloads.append(
        WorkloadDefinition(
            workload_id="workload_e_dataset_summary_monetdb",
            operation="aggregate_dataset_summary",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            func=lambda: monetdb_adapter.get_dataset_summary(),
        )
    )

    return workloads


def verify_cross_database_correctness(
    neo4j_adapter: Neo4jBenchmarkAdapter,
    monetdb_adapter: MonetDBBenchmarkAdapter,
    movie_id: int = 217465,
) -> List[CorrectnessComparison]:
    """
    Compare equivalent queries between Neo4j and MonetDB to ensure logical agreement.
    """
    comparisons: List[CorrectnessComparison] = []

    # 1. Movie Lookup
    _, n_movie = neo4j_adapter.get_movie_by_id(movie_id)
    _, m_movie = monetdb_adapter.get_movie_by_id(movie_id)

    lookup_match = False
    details = None
    if n_movie and m_movie:
        lookup_match = (
            n_movie["movie_id"] == m_movie["movie_id"]
            and n_movie["title"].strip() == m_movie["title"].strip()
            and n_movie.get("year") == m_movie.get("year")
        )
    else:
        details = f"Neo4j: {bool(n_movie)}, MonetDB: {bool(m_movie)}"

    comparisons.append(
        CorrectnessComparison(
            workload_id="workload_a_lookup",
            operation="lookup_movie_by_id",
            neo4j_count=1 if n_movie else 0,
            monetdb_count=1 if m_movie else 0,
            counts_match=(bool(n_movie) == bool(m_movie)),
            data_matches=lookup_match,
            discrepancy_details=details,
        )
    )

    # 2. Movie Genres
    _, n_genres = neo4j_adapter.get_genres_for_movie(movie_id)
    _, m_genres = monetdb_adapter.get_genres_for_movie(movie_id)

    set_n = set(n_genres or [])
    set_m = set(m_genres or [])
    genres_match = (set_n == set_m)

    comparisons.append(
        CorrectnessComparison(
            workload_id="workload_c_genres",
            operation="get_movie_genres",
            neo4j_count=len(set_n),
            monetdb_count=len(set_m),
            counts_match=(len(set_n) == len(set_m)),
            data_matches=genres_match,
            discrepancy_details=None if genres_match else f"Neo4j: {set_n} vs MonetDB: {set_m}",
        )
    )

    return comparisons
