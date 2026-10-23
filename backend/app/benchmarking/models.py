"""Benchmarking data models and schemas."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    DATABASE_QUERY = "database_query"
    API_REQUEST = "api_request"


class TargetEngine(str, Enum):
    NEO4J = "neo4j"
    MONETDB = "monetdb"
    FASTAPI = "fastapi"


class BenchmarkConfig(BaseModel):
    """Runtime configuration for a benchmark execution."""
    warmup_iterations: int = Field(default=3, ge=0)
    measured_iterations: int = Field(default=10, ge=1)
    concurrency_levels: List[int] = Field(default_factory=lambda: [1, 2, 5, 10])
    timeout_seconds: float = Field(default=30.0, gt=0)
    random_seed: int = Field(default=42)
    output_dir: str = Field(default="reports/phase-5/results")


class RawMeasurement(BaseModel):
    """A single measured query or request event."""
    timestamp: datetime
    run_id: str
    workload_id: str
    operation: str
    target_engine: TargetEngine
    execution_mode: ExecutionMode
    repetition_index: int
    is_warmup: bool
    duration_ms: float
    success: bool
    result_count: int
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkloadMetrics(BaseModel):
    """Aggregate statistics for a specific benchmark operation."""
    workload_id: str
    operation: str
    target_engine: TargetEngine
    execution_mode: ExecutionMode
    repetition_count: int
    success_count: int
    error_count: int
    error_rate_pct: float
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    p90_ms: float
    p95_ms: float
    stddev_ms: float
    throughput_ops_per_sec: float
    avg_result_count: float


class CorrectnessComparison(BaseModel):
    """Results of comparing equivalent queries across Neo4j and MonetDB."""
    workload_id: str
    operation: str
    neo4j_count: int
    monetdb_count: int
    counts_match: bool
    data_matches: bool
    discrepancy_details: Optional[str] = None


class RecommendationEvalMetrics(BaseModel):
    """Offline recommendation evaluation results across ranking metrics."""
    model_name: str
    k: int
    precision: float
    recall: float
    ndcg: float
    hit_rate: float
    catalog_coverage: float
    eligible_users_count: int
    evaluated_interactions_count: int


class RunManifest(BaseModel):
    """Metadata describing a benchmark run and the operating environment."""
    run_id: str
    timestamp: datetime
    git_commit: Optional[str] = None
    python_version: str
    dataset_metadata: Dict[str, Any]
    config: BenchmarkConfig
    summary_metrics_file: str
    raw_measurements_file: str
