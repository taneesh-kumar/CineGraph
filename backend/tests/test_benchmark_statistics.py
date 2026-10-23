"""Unit tests for benchmarking statistics, storage, and models."""
import math
import pytest
from app.benchmarking.models import (
    RawMeasurement,
    TargetEngine,
    ExecutionMode,
    BenchmarkConfig,
)
from app.benchmarking.statistics import calculate_percentile, calculate_metrics
from app.benchmarking.storage import BenchmarkStorage
from datetime import datetime


def test_calculate_percentile():
    data = [10.0, 20.0, 30.0, 40.0, 50.0]
    # Median
    assert calculate_percentile(data, 50.0) == 30.0
    # Min & Max
    assert calculate_percentile(data, 0.0) == 10.0
    assert calculate_percentile(data, 100.0) == 50.0
    # Interpolated
    p25 = calculate_percentile(data, 25.0)
    assert p25 == 20.0
    p75 = calculate_percentile(data, 75.0)
    assert p75 == 40.0


def test_calculate_metrics_success():
    measurements = [
        # Warmup (should be ignored in latency)
        RawMeasurement(
            timestamp=datetime.utcnow(),
            run_id="test",
            workload_id="w1",
            operation="op",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            repetition_index=0,
            is_warmup=True,
            duration_ms=100.0,
            success=True,
            result_count=1,
        ),
        # Measured reps
        RawMeasurement(
            timestamp=datetime.utcnow(),
            run_id="test",
            workload_id="w1",
            operation="op",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            repetition_index=0,
            is_warmup=False,
            duration_ms=10.0,
            success=True,
            result_count=1,
        ),
        RawMeasurement(
            timestamp=datetime.utcnow(),
            run_id="test",
            workload_id="w1",
            operation="op",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            repetition_index=1,
            is_warmup=False,
            duration_ms=20.0,
            success=True,
            result_count=1,
        ),
        RawMeasurement(
            timestamp=datetime.utcnow(),
            run_id="test",
            workload_id="w1",
            operation="op",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            repetition_index=2,
            is_warmup=False,
            duration_ms=30.0,
            success=True,
            result_count=1,
        ),
    ]

    metrics = calculate_metrics(measurements)
    assert metrics.repetition_count == 3
    assert metrics.success_count == 3
    assert metrics.error_count == 0
    assert metrics.error_rate_pct == 0.0
    assert metrics.min_ms == 10.0
    assert metrics.max_ms == 30.0
    assert metrics.mean_ms == 20.0
    assert metrics.median_ms == 20.0
    assert metrics.throughput_ops_per_sec == 50.0  # 1000 / 20.0


def test_calculate_metrics_with_errors():
    measurements = [
        RawMeasurement(
            timestamp=datetime.utcnow(),
            run_id="test",
            workload_id="w1",
            operation="op",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            repetition_index=0,
            is_warmup=False,
            duration_ms=15.0,
            success=True,
            result_count=5,
        ),
        RawMeasurement(
            timestamp=datetime.utcnow(),
            run_id="test",
            workload_id="w1",
            operation="op",
            target_engine=TargetEngine.MONETDB,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            repetition_index=1,
            is_warmup=False,
            duration_ms=0.0,
            success=False,
            result_count=0,
            error_message="Connection timed out",
        ),
    ]

    metrics = calculate_metrics(measurements)
    assert metrics.repetition_count == 2
    assert metrics.success_count == 1
    assert metrics.error_count == 1
    assert metrics.error_rate_pct == 50.0
    assert metrics.mean_ms == 15.0


def test_benchmark_storage(tmp_path):
    storage = BenchmarkStorage(base_output_dir=str(tmp_path))
    measurements = [
        RawMeasurement(
            timestamp=datetime.utcnow(),
            run_id="run-1",
            workload_id="w1",
            operation="op",
            target_engine=TargetEngine.NEO4J,
            execution_mode=ExecutionMode.DATABASE_QUERY,
            repetition_index=0,
            is_warmup=False,
            duration_ms=12.5,
            success=True,
            result_count=1,
            parameters={"param": "val"},
        )
    ]
    csv_file = storage.save_raw_measurements("run-1", measurements)
    assert csv_file.exists()
    assert csv_file.stat().st_size > 0

    runs = storage.list_runs()
    assert "1" in runs
