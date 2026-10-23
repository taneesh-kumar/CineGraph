"""Statistical calculations for benchmarking latency and throughput."""
import math
from typing import List
from app.benchmarking.models import RawMeasurement, WorkloadMetrics


def calculate_percentile(sorted_data: List[float], percentile: float) -> float:
    """
    Calculate the p-th percentile from an already sorted list of floats using linear interpolation.
    percentile is between 0.0 and 100.0.
    """
    if not sorted_data:
        return 0.0
    if len(sorted_data) == 1:
        return sorted_data[0]

    n = len(sorted_data)
    rank = (percentile / 100.0) * (n - 1)
    k = math.floor(rank)
    d = rank - k
    if k + 1 < n:
        return sorted_data[k] + d * (sorted_data[k + 1] - sorted_data[k])
    return sorted_data[k]


def calculate_metrics(measurements: List[RawMeasurement]) -> WorkloadMetrics:
    """
    Compute statistical metrics for a collection of measurements of the same operation.
    Only non-warmup measurements are used for latency calculations.
    """
    if not measurements:
        raise ValueError("Cannot compute metrics for empty measurement list.")

    first = measurements[0]
    valid_measurements = [m for m in measurements if not m.is_warmup]
    if not valid_measurements:
        valid_measurements = measurements  # fallback if all were warmups

    durations = [m.duration_ms for m in valid_measurements if m.success]
    total_reps = len(valid_measurements)
    successes = len(durations)
    errors = total_reps - successes
    error_rate = (errors / total_reps * 100.0) if total_reps > 0 else 0.0

    if not durations:
        return WorkloadMetrics(
            workload_id=first.workload_id,
            operation=first.operation,
            target_engine=first.target_engine,
            execution_mode=first.execution_mode,
            repetition_count=total_reps,
            success_count=0,
            error_count=errors,
            error_rate_pct=100.0,
            min_ms=0.0,
            max_ms=0.0,
            mean_ms=0.0,
            median_ms=0.0,
            p90_ms=0.0,
            p95_ms=0.0,
            stddev_ms=0.0,
            throughput_ops_per_sec=0.0,
            avg_result_count=0.0,
        )

    durations.sort()
    n = len(durations)
    mean_val = sum(durations) / n
    variance = sum((x - mean_val) ** 2 for x in durations) / n if n > 0 else 0.0
    stddev_val = math.sqrt(variance)

    min_val = durations[0]
    max_val = durations[-1]
    median_val = calculate_percentile(durations, 50.0)
    p90_val = calculate_percentile(durations, 90.0)
    p95_val = calculate_percentile(durations, 95.0)

    # Throughput (ops/sec) = 1000.0 / mean_ms
    throughput = (1000.0 / mean_val) if mean_val > 0 else 0.0

    results_counts = [m.result_count for m in valid_measurements if m.success]
    avg_count = sum(results_counts) / len(results_counts) if results_counts else 0.0

    return WorkloadMetrics(
        workload_id=first.workload_id,
        operation=first.operation,
        target_engine=first.target_engine,
        execution_mode=first.execution_mode,
        repetition_count=total_reps,
        success_count=successes,
        error_count=errors,
        error_rate_pct=round(error_rate, 2),
        min_ms=round(min_val, 3),
        max_ms=round(max_val, 3),
        mean_ms=round(mean_val, 3),
        median_ms=round(median_val, 3),
        p90_ms=round(p90_val, 3),
        p95_ms=round(p95_val, 3),
        stddev_ms=round(stddev_val, 3),
        throughput_ops_per_sec=round(throughput, 2),
        avg_result_count=round(avg_count, 1),
    )
