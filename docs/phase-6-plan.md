# CineGraph — Phase 6 Implementation & Validation Plan
## Final Validation, Reliability Audit, Reproducibility, Documentation & Project Delivery

### 1. Project Context & Status Baseline
- **Repository Root**: `T:\Taneesh\Documents\Git Repos\CineGraph`
- **Architecture**:
  - Frontend: Next.js 16 (App Router), TypeScript, Tailwind CSS, Lucide Icons.
  - Backend: FastAPI, Python 3.11, Uvicorn ASGI server.
  - Graph Engine: Neo4j 5.26.0 (Bolt port 7687, HTTP port 7474) in Docker.
  - Columnar Engine: MonetDB (MAPI port 50000) in Docker.
  - Benchmarking: Native execution adapters, monotonic statistics, offline temporal evaluator, matplotlib visualizer.
- **Active Dataset**: MovieLens 32M Sample (2020–2023 filter): **2,500 movies**, **119,689 ratings**, **18,327 users**, **16 genres**, **25,999 tags**.
- **Current Baseline Status**:
  - Live Docker containers: `cinegraph-neo4j` (healthy), `cinegraph-monetdb` (healthy).
  - Live Backend (`http://127.0.0.1:8000/ready`): Dual engines connected and ready.
  - Live Frontend (`http://localhost:3000`): HTTP 200 OK.
  - Backend test suite: 68 passed, 0 failed.
  - Frontend test suite: 11 passed, 0 failed.

---

### 2. Phase 6 Execution Checklist

- [ ] **Phase 6.0: Repository Baseline & Change Audit**
  - Verify clean working tree (`git status`).
  - Document baseline status in `docs/phase-6-plan.md`.

- [ ] **Phase 6.1: Environment & Clean-Start Validation**
  - Verify `docker-compose.yml` config, port bindings, volumes, and healthchecks.
  - Verify `.env.example` safe placeholder defaults.
  - Verify backend startup command & dependency requirements.
  - Verify frontend dev/build workflow.

- [ ] **Phase 6.2: Database, Ingestion & Data-Integrity Audit**
  - Re-verify cross-database parity non-destructively using `app.ingestion.verify`.
  - Confirm zero dangling relationships, zero duplicate PKs, and consistent entity counts.

- [ ] **Phase 6.3: API & End-to-End Functional Validation**
  - Create automated smoke test script `scripts/smoke_test.py` covering all 10 essential application flows:
    1. Health (`/health`)
    2. Readiness (`/ready`)
    3. Dataset Summary (`/api/v1/analytics/summary`)
    4. Top-Rated Movies (`/api/v1/analytics/top-rated`)
    5. Genre Popularity (`/api/v1/analytics/genres`)
    6. Rating Distribution (`/api/v1/analytics/ratings/distribution`)
    7. Movie Detail (`/api/v1/movies/{id}`)
    8. Movie Rating Stats (`/api/v1/analytics/movies/{id}/ratings`)
    9. Movie Search (`/api/v1/movies/search`)
    10. Graph Recommendations (`/api/v1/recommendations/movie/{id}` and `/user/{id}`)
  - Execute smoke tests against live services.

- [ ] **Phase 6.4: Benchmarking & Recommendation Evaluation Audit**
  - Verify reproducibility of Phase 5 benchmark suite (`scripts/run_benchmarks.py`).
  - Audit offline recommendation evaluation methodology (train/test temporal split, zero future leakage).
  - Validate figure generation and result artifact persistence.

- [ ] **Phase 6.5: Security & Configuration Review**
  - Inspect `.gitignore` for `.env`, secret files, build artifacts.
  - Verify credentials are parameterized and no secrets are committed.
  - Confirm error responses do not leak database connection strings or internal stack traces.

- [ ] **Phase 6.6: Documentation & Reproducibility**
  - Update root `README.md` with complete architecture, dual-engine rationale, setup commands, and reproducible steps.
  - Ensure `docs/architecture.md` includes system architecture and data-flow diagrams.
  - Update `docs/benchmarking.md` and `docs/recommendation-evaluation.md`.

- [ ] **Phase 6.7: Final Regression & Build Gate**
  - Run full backend test suite (`pytest -v`).
  - Run frontend unit tests (`npm test`).
  - Run frontend linter (`npm run lint`).
  - Run frontend production build (`npm run build`).

- [ ] **Phase 6.8: Academic Demonstration Preparation**
  - Create `docs/final-demo-guide.md` with a structured, step-by-step presentation script.

- [ ] **Phase 6.9: Phase 6 Final Report**
  - Create `reports/phase-6/phase-6-final-report.md` detailing all verified evidence and status.
