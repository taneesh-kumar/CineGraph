"""Concurrency load testing harness and execution engine."""
import asyncio
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Tuple
import httpx
from app.benchmarking.models import (
    RawMeasurement,
    TargetEngine,
    ExecutionMode,
    WorkloadMetrics,
    BenchmarkConfig,
)
from app.benchmarking.statistics import calculate_metrics
from app.benchmarking.workloads import WorkloadDefinition


class BenchmarkRunner:
    """Orchestrates warmup, steady-state repetitions, and metrics aggregation."""

    def __init__(self, config: BenchmarkConfig, run_id: str):
        self.config = config
        self.run_id = run_id

    def run_workload(self, workload: WorkloadDefinition) -> Tuple[List[RawMeasurement], WorkloadMetrics]:
        """Execute a workload through warm-up and measured iterations."""
        measurements: List[RawMeasurement] = []

        # 1. Warm-up iterations (discarded from latency statistics)
        for i in range(self.config.warmup_iterations):
            try:
                dur_ms, res = workload.func()
                res_count = len(res) if isinstance(res, (list, tuple, set)) else (1 if res else 0)
                measurements.append(
                    RawMeasurement(
                        timestamp=datetime.utcnow(),
                        run_id=self.run_id,
                        workload_id=workload.workload_id,
                        operation=workload.operation,
                        target_engine=workload.target_engine,
                        execution_mode=workload.execution_mode,
                        repetition_index=i,
                        is_warmup=True,
                        duration_ms=round(dur_ms, 3),
                        success=True,
                        result_count=res_count,
                        parameters=workload.parameters,
                    )
                )
            except Exception as e:
                measurements.append(
                    RawMeasurement(
                        timestamp=datetime.utcnow(),
                        run_id=self.run_id,
                        workload_id=workload.workload_id,
                        operation=workload.operation,
                        target_engine=workload.target_engine,
                        execution_mode=workload.execution_mode,
                        repetition_index=i,
                        is_warmup=True,
                        duration_ms=0.0,
                        success=False,
                        result_count=0,
                        error_message=str(e),
                        parameters=workload.parameters,
                    )
                )

        # 2. Measured steady-state repetitions
        for i in range(self.config.measured_iterations):
            try:
                dur_ms, res = workload.func()
                res_count = len(res) if isinstance(res, (list, tuple, set)) else (1 if res else 0)
                measurements.append(
                    RawMeasurement(
                        timestamp=datetime.utcnow(),
                        run_id=self.run_id,
                        workload_id=workload.workload_id,
                        operation=workload.operation,
                        target_engine=workload.target_engine,
                        execution_mode=workload.execution_mode,
                        repetition_index=i,
                        is_warmup=False,
                        duration_ms=round(dur_ms, 3),
                        success=True,
                        result_count=res_count,
                        parameters=workload.parameters,
                    )
                )
            except Exception as e:
                measurements.append(
                    RawMeasurement(
                        timestamp=datetime.utcnow(),
                        run_id=self.run_id,
                        workload_id=workload.workload_id,
                        operation=workload.operation,
                        target_engine=workload.target_engine,
                        execution_mode=workload.execution_mode,
                        repetition_index=i,
                        is_warmup=False,
                        duration_ms=0.0,
                        success=False,
                        result_count=0,
                        error_message=str(e),
                        parameters=workload.parameters,
                    )
                )

        metrics = calculate_metrics(measurements)
        return measurements, metrics


async def run_concurrency_benchmark(
    base_url: str = "http://127.0.0.1:8000",
    concurrency_levels: List[int] = [1, 2, 5, 10],
    requests_per_level: int = 20,
) -> List[Dict[str, Any]]:
    """
    Measure FastAPI throughput and latency across controlled concurrency levels.
    Endpoint tested: /api/v1/recommendations/movie/217465?limit=5 (Tenet)
    """
    results: List[Dict[str, Any]] = []
    target_endpoint = f"{base_url}/api/v1/recommendations/movie/217465?limit=5"

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Pre-warm
        try:
            await client.get(target_endpoint)
        except Exception:
            pass

        for c in concurrency_levels:
            sem = asyncio.Semaphore(c)
            durations: List[float] = []
            errors = 0

            async def make_request():
                nonlocal errors
                async with sem:
                    start = time.perf_counter()
                    try:
                        resp = await client.get(target_endpoint)
                        dur = (time.perf_counter() - start) * 1000.0
                        if resp.status_code == 200:
                            durations.append(dur)
                        else:
                            errors += 1
                    except Exception:
                        errors += 1

            start_batch = time.perf_counter()
            tasks = [asyncio.create_task(make_request()) for _ in range(requests_per_level)]
            await asyncio.gather(*tasks)
            total_time_sec = time.perf_counter() - start_batch

            durations.sort()
            n = len(durations)
            mean_ms = sum(durations) / n if n > 0 else 0.0
            median_ms = durations[n // 2] if n > 0 else 0.0
            p95_ms = durations[int(n * 0.95)] if n > 0 else 0.0
            throughput = (n / total_time_sec) if total_time_sec > 0 else 0.0

            results.append({
                "concurrency": c,
                "total_requests": requests_per_level,
                "successful_requests": n,
                "errors": errors,
                "total_time_sec": round(total_time_sec, 3),
                "throughput_req_per_sec": round(throughput, 2),
                "mean_latency_ms": round(mean_ms, 2),
                "median_latency_ms": round(median_ms, 2),
                "p95_latency_ms": round(p95_ms, 2),
            })

    return results
