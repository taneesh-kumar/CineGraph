# CineGraph Phase 5 Implementation Plan
## Database Performance Benchmarking, Recommendation Evaluation, and Experimental Analysis

### 1. Context & Objectives
Phase 5 establishes a defensible, reproducible benchmark and evaluation system addressing:
1. Performance of Neo4j (graph workloads) vs MonetDB (columnar aggregations).
2. Scaling and latency variations under controlled concurrency and workload complexity.
3. Offline recommendation system utility (Hit Rate, Precision, Recall, NDCG, Coverage) using time-ordered held-out test splits without data leakage.
4. Latency vs. quality trade-offs between graph topology traversal and tabular/columnar filtering.
5. Evidence-based architectural insights from live measurements.

---

### 2. Execution Checklist

- [ ] **Phase 5.0: Baseline Discovery**
  - Verify database readiness and active dataset metrics (2,500 movies, 18,327 users, 119,689 ratings).
  - Verify baseline backend tests (62 passing) and frontend build.
  - Document baseline status in `docs/phase-5-plan.md`.

- [ ] **Phase 5.1: Reproducible Benchmark Framework**
  - Create `backend/app/benchmarking/` package:
    - `models.py`: Pydantic models for `BenchmarkConfig`, `RawMeasurement`, `WorkloadMetrics`, `RunManifest`.
    - `statistics.py`: High-resolution timing, percentiles (median, p90, p95, min, max, stddev), error rates.
    - `storage.py`: JSONL raw measurement persistence, JSON aggregate summaries, run manifests.
    - `adapters/neo4j_adapter.py`: Direct driver session queries with session reuse.
    - `adapters/monetdb_adapter.py`: Connection pool / cursor execution.
    - `adapters/api_adapter.py`: Async HTTP requests via `httpx.AsyncClient`.
    - `workloads.py`: Comparable, native, and API workload definitions (A to G).
    - `runner.py`: Benchmark execution engine with warm-up cycles, steady-state repetitions, and error handling.
    - `reporting.py`: Markdown and console summary generation.

- [ ] **Phase 5.2: Database Workloads & Correctness Verification**
  - Workload A: Entity Lookup (Movie by ID - Neo4j vs MonetDB parity).
  - Workload B: Title Search (Broad vs selective vs no-match substring searches).
  - Workload C: Genre Relationships (Movie genres and genre movie lists).
  - Workload D: Graph Traversals (Users who rated, movies rated by user, common neighbor traversal).
  - Workload E: Analytical Aggregations (Rating counts, avg rating, top-rated movies, genre totals, distributions).
  - Workload F: Recommendation API (`/movie/{id}` and `/user/{id}`).
  - Workload G: Analytics API (`/top-rated`, `/genres`, `/ratings/distribution`, `/movies/{id}/ratings`, `/summary`).
  - Automated correctness comparator between cross-database workloads.

- [ ] **Phase 5.3: Concurrency & Scalability**
  - Asynchronous concurrent load harness (concurrency levels: 1, 2, 5, 10).
  - Collect throughput (requests/sec), latency percentiles, and error rate.
  - Process-level resource measurement (CPU/RAM where available).

- [ ] **Phase 5.4: Recommendation Quality Evaluation**
  - Create `backend/app/benchmarking/evaluator.py`:
    - Offline evaluation protocol using user rating histories.
    - Temporal / per-user split (earlier ratings for user profile, later ratings for test evaluation) to prevent data leakage.
    - Relevance definition: Rating >= 4.0 in held-out interactions.
    - Ranking metrics: Precision@K, Recall@K, NDCG@K, HitRate@K, Catalog Coverage for K = 5 and K = 10.
    - Baselines: Global Popularity, Genre Match, Collaborative/Graph Recommender.

- [ ] **Phase 5.5: Visualizations & Reports**
  - Create `backend/app/benchmarking/visualizer.py` generating figures:
    - Query latency comparison (Neo4j vs MonetDB).
    - Percentile distributions (p50, p90, p95).
    - Concurrency vs throughput scaling.
    - Recommendation metrics across models.
  - Save reports and figures in `reports/phase-5/`.

- [ ] **Phase 5.6: CLI Runner & Scripts**
  - CLI script: `backend/app/benchmarking/cli.py` and root runner `scripts/run_benchmarks.py`.

- [ ] **Phase 5.7: Testing & Quality Assurance**
  - Unit tests for benchmark statistics, storage, metrics calculation, and evaluator.
  - Regression check: Ensure all 62 existing tests continue to pass.
  - Documentation: Update `docs/benchmarking.md` and `docs/recommendation-evaluation.md`.
