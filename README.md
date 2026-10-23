# CineGraph

> **Hybrid NoSQL Movie Recommendations and Columnar Trend Analytics**  
> An academic course project uniting **Neo4j** (Graph Database) and **MonetDB** (Column-Store Analytical Database) with a **FastAPI** backend and **Next.js** frontend.

---

## 1. What is CineGraph?

**CineGraph** is a full-stack movie intelligence platform designed to explore and benchmark the strengths of different NoSQL and analytical database paradigms.

By using both a native graph database and a native column-store engine side-by-side, CineGraph enables:
- **Graph-Powered Discovery**: Seamless traversal of actors, directors, genres, and user rating topologies to produce personalized recommendations and co-occurrence networks.
- **High-Velocity Aggregations**: Sub-second execution of complex analytical queries across millions of ratings (e.g., genre popularity trends across decades, release-year distribution).
- **Comparative Benchmarking**: Academic evaluation comparing query runtimes between graph traversals and columnar SQL aggregations on identical analytical workloads.

---

## 2. Why Neo4j and MonetDB?

| Database Engine | Type | Primary Role in CineGraph | Why It Was Chosen |
|---|---|---|---|
| **Neo4j Community** | Graph Database | Entity relationships, paths, personalized recommendations | Graph databases excel at interconnected queries (e.g., "Find movies directed by Nolan starring actors who worked with Christian Bale") without costly multiple table JOINs. |
| **MonetDB** | Columnar SQL Engine | Trend analytics, distribution aggregations, reporting | Column-stores read only the queried columns (e.g., `rating`, `release_year`, `genre`), drastically reducing I/O and computing aggregate metrics across large datasets exponentially faster than row-oriented or pure graph databases. |

---

## 3. Technology Stack

- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS.
- **Backend**: Python 3.11/3.12+, FastAPI, Pydantic v2, Uvicorn, Pytest.
- **Graph Database**: Neo4j Community Edition `5.26.0` (Docker container).
- **Analytical Database**: MonetDB `latest` (Docker container).
- **Orchestration**: Docker Compose.
- **Package Managers**: npm (frontend), pip / venv (backend).

---

## 4. Repository Structure

```text
CineGraph/
├── frontend/                     # Next.js App Router Web UI
│   ├── app/                      # Page components, layouts, global styling
│   ├── public/                   # Static assets & icons
│   ├── package.json              # Frontend dependencies and build scripts
│   └── README.md                 # Frontend-specific documentation
├── backend/                      # FastAPI Python REST API
│   ├── app/                      # Application modular core
│   │   ├── api/                  # Route handlers (health, root, future endpoints)
│   │   ├── core/                 # Config & settings (pydantic-settings)
│   │   └── main.py               # FastAPI application entrypoint
│   ├── tests/                    # Backend test suite (pytest)
│   ├── requirements.txt          # Python dependencies
│   ├── .python-version           # Target Python runtime
│   └── README.md                 # Backend-specific documentation
├── docker/                       # Database container notes & helpers
│   └── README.md                 # Docker setup & MonetDB initialization guide
├── docs/                         # Project architecture and technical design
│   ├── architecture.md           # System blueprint and component interactions
│   ├── database-design.md        # Neo4j and MonetDB schemas and query patterns
│   └── development-setup.md      # Comprehensive local environment setup guide
├── .env.example                  # Environment template with placeholder secrets
├── .gitignore                    # Git exclusion rules (secrets, venvs, builds)
├── docker-compose.yml            # Multi-container database definitions
├── LICENSE_DECISION.md           # Licensing rationale (MIT)
└── README.md                     # Root project documentation
```

---

## 5. Prerequisites

Before starting CineGraph locally, install:
- **Node.js** (v20+ LTS recommended, tested on Node v25 / npm v11)
- **Python** (3.11 or 3.12+ recommended)
- **Docker Desktop** (with Docker Compose v2+)
- **Git**

---

## 6. Setup Instructions

### Step 1: Clone and Configure Environment

```bash
# Clone the repository (or navigate to existing directory)
cd CineGraph

# Create local environment configuration from template
cp .env.example .env
# (On Windows PowerShell: Copy-Item .env.example .env)
```

> **IMPORTANT**: Set secure passwords in `.env`. Never commit `.env` to version control.

---

### Step 2: Start the Databases (Docker Compose)

Start Neo4j and MonetDB in detached mode:

```bash
docker compose up -d
```

Verify that the containers are healthy and running:

```bash
docker compose ps
```

- **Neo4j Web Browser**: [http://127.0.0.1:7474](http://127.0.0.1:7474) (Bolt: `bolt://127.0.0.1:7687`)
- **MonetDB MAPI**: `127.0.0.1:50000`

---

### Step 3: Start the Backend (FastAPI)

In a separate terminal:

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automated tests
pytest

# Launch development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Interactive API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Step 4: Run MovieLens Data Ingestion (Phase 2)

CineGraph includes a streaming, idempotent data ingestion pipeline that synchronizes `ml-32m` into both Neo4j and MonetDB.

```bash
cd backend

# 1. Validate dataset preflight integrity
python -m app.ingestion.cli --validate-only

# 2. Ingest development sample (e.g. 1,000 movies and corresponding ratings/tags)
python -m app.ingestion.cli --sample-limit 1000 --batch-size 1000

# 3. Verify cross-database integrity and consistency
python -m app.ingestion.verify

# 4. Optional: Ingest full dataset (32M ratings, bounded batches)
# python -m app.ingestion.cli --sample-limit 0 --batch-size 5000
```

---

### Step 5: Start the Frontend (Next.js)

In another terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Step 6: Run Tests & Verification

#### Automated Smoke Tests
Exercise the complete end-to-end API against the live system:
```bash
python scripts/smoke_test.py
```

#### Backend Test Suite (Pytest)
```bash
cd backend
.venv\Scripts\pytest -v
```

#### Frontend Test Suite (Node test runner)
```bash
cd frontend
npm test
npm run build
```

#### Database Benchmarks & Recommendation Evaluation
Run the reproducible Phase 5 benchmark suite and generate 2D charts:
```bash
python scripts/run_benchmarks.py run --warmup 2 --repetitions 5 --eval-users 25
```
Results and charts are saved directly to `reports/phase-5/`.

---

## 7. Managing Database Containers and Persistence

### Stopping Containers (Preserving Data)
To stop the database containers without losing stored graphs or analytical tables:
```bash
docker compose stop
# or
docker compose down
```
> Persistent Docker named volumes (`cinegraph_neo4j_data`, `cinegraph_monetdb_data`) remain intact.

### Inspecting Logs
```bash
docker compose logs -f neo4j
docker compose logs -f monetdb
```

### Complete Reset (Data-Preserving Cleanup vs. Total Purge)
If you wish to wipe all data and start completely fresh:
```bash
# CAUTION: This deletes all database volumes and data permanently
docker compose down -v
```

---

## 8. Current Implementation Status & Roadmap

| Feature / Area | Status | Description |
|---|---|---|
| **Repository Foundation** | ✅ Completed | Structure, build setups, environment configs, documentation |
| **FastAPI Backend** | ✅ Completed | Versioned REST API (`/api/v1`), dependency injection, health & ready probes, 68 automated tests |
| **Dual Database Integration** | ✅ Completed | Isolated Neo4j Community (7687) & MonetDB (50000) with verified entity parity |
| **MovieLens Ingestion Pipeline** | ✅ Completed | Streaming, idempotent dual-database ingestion pipeline with preflight and sample modes |
| **Recommendation Engine**| ✅ Completed | Neo4j Cypher graph queries: content genre similarity & personalized collaborative community walks |
| **Analytics Dashboard** | ✅ Completed | MonetDB vectorized aggregations: Top-rated movies with threshold filters, genre popularity, rating distributions |
| **Complete Web Frontend** | ✅ Completed | Next.js 16 App Router UI with Movie Discovery, Recommendations, Analytics, System Status, 11 tests |
| **Performance Benchmark**| ✅ Completed | Automated timing, percentile analysis, and offline recommendation evaluator with matplotlib visualizations |
| **Validation & Hardening**| ✅ Completed | Live smoke testing, non-destructive parity audit, and demonstration script |
