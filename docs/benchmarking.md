# CineGraph Database Benchmarking Guide

This document describes the reproducible benchmarking and evaluation framework implemented in Phase 5 of CineGraph.

## Architecture

The benchmarking subsystem is located in `backend/app/benchmarking/` and consists of:
- **`models.py`**: Pydantic models for run configuration, raw event tracking, percentile metrics, and manifest records.
- **`statistics.py`**: Monotonic timing and percentile interpolation (`min`, `median`, `mean`, `max`, `p90`, `p95`, `stddev`).
- **`adapters.py`**: Native execution wrappers for `Neo4jRepository` and `MonetDBRepository`.
- **`workloads.py`**: Standardized definitions for Workloads A through E, plus cross-database correctness verifiers.
- **`runner.py`**: Benchmark runner managing warm-up discarding, repetition batches, and concurrency loads.
- **`evaluator.py`**: Offline recommendation quality evaluator using time-ordered splits to prevent test leakage.
- **`visualizer.py`**: Matplotlib figure generator for 2D charts and percentile graphs.
- **`storage.py`**: Multi-run artifact persistence (JSON summaries, raw CSV logs, and manifests).
- **`cli.py`**: Command-line interface.

## Running Benchmarks

### Full Suite Run
```powershell
backend\.venv\Scripts\python scripts\run_benchmarks.py run --warmup 2 --repetitions 10 --eval-users 30
```

Options:
- `--warmup`: Number of initial cycles executed and excluded from statistics (default: `3`).
- `--repetitions`: Number of steady-state iterations measured (default: `10`).
- `--eval-users`: Number of eligible user rating histories to evaluate for recommendation quality (default: `30`).
- `--output-dir`: Results directory (default: `reports/phase-5/results`).
- `--figures-dir`: Chart output directory (default: `reports/phase-5/figures`).

## Output Artifacts

Each execution generates a uniquely timestamped folder in `reports/phase-5/results/run-<TIMESTAMP>/`:
1. `raw-benchmarks.csv`: Complete row-by-row event log of every repetition, duration, engine, and query parameter.
2. `benchmark-summary.json`: Aggregated latency statistics and throughput calculations per workload.
3. `correctness-results.json`: Cross-database parity results on identical entities.
4. `recommendation-evaluation.json`: Precision, Recall, NDCG, Hit Rate, and Coverage metrics for recommenders.
5. `manifest.json`: Execution metadata including environment, Python version, and dataset counts.
