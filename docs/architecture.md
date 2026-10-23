# CineGraph Architecture Document

## 1. Overview & Project Goals

**CineGraph** is a hybrid NoSQL academic and analytical movie intelligence platform. The primary goal of the system is to leverage the strengths of two distinct database paradigms:
- **Neo4j** (Graph Database): To traverse complex relationship topologies, power actor/director/user recommendations, and perform graph centrality analysis.
- **MonetDB** (Column-Store Analytical Database): To execute aggregate SQL queries across massive tabular datasets (e.g., ratings distributions, genre breakdown over decades, release-year metrics) with sub-second columnar query performance.

---

## 2. Architectural Blueprint

```
+-------------------------------------------------------+
|                 Next.js Frontend                      |
| (TypeScript, React 19, Tailwind CSS, Component UI)    |
+---------------------------+---------------------------+
                            | HTTP / JSON REST
                            v
+-------------------------------------------------------+
|                  FastAPI Backend                      |
|    - Routing, Input Validation (Pydantic)             |
|    - Connection Pooling & Adapter Layer               |
|    - Unified API Response Orchestration               |
+--------------+--------------------------+-------------+
               |                          |
       Bolt Protocol (7687)        MAPI / SQL (50000)
               |                          |
               v                          v
+-----------------------------+ +-----------------------+
|       Neo4j Community       | |   MonetDB Columnar    |
|   - Nodes: Movie, Actor,    | | - Tables: ratings,    |
|     Director, User, Genre   | |   movies, genres,     |
|   - Edges: :ACTED_IN,       | |   tags                |
|     :DIRECTED, :RATED       | | - Aggregations, OLAP, |
|   - Recommendation & Paths  | |   Yearly Trend Analys.|
+-----------------------------+ +-----------------------+
               ^                          ^
               |                          |
+--------------+--------------------------+-------------+
|          MovieLens Ingestion Pipeline (Planned)       |
|    - Parses MovieLens ml-latest-small / ml-25m        |
|    - Hydrates Graph Entities into Neo4j               |
|    - Bulk Loads Analytical Columns into MonetDB       |
+-------------------------------------------------------+
```

---

## 3. Technology Stack & Component Responsibilities

### 3.1 Frontend (Next.js & Tailwind CSS)
- **Framework**: Next.js (App Router), React, TypeScript.
- **Styling**: Tailwind CSS for responsive and modern interface styling.
- **Role**:
  - Delivers dynamic search and discovery UI.
  - Interactive graph visualizations (future).
  - Analytical charts and benchmark dashboards (future).
  - *Strict Rule*: The browser communicates solely with the FastAPI backend; it **never** connects directly to Neo4j or MonetDB.

### 3.2 Backend (FastAPI & Python)
- **Framework**: FastAPI with clean layered separation of concerns.
- **Settings**: Strongly typed configuration via `pydantic-settings` reading from `.env`.
- **Database Access & Lifecycle**:
  - `app/core/database.py`: Unified `DatabaseManager` providing singleton Neo4j driver with auto-closing lifespan and managed MonetDB connection/cursor context managers.
  - `app/repositories/neo4j_repo.py`: Parameterized Cypher queries isolating graph traversals from route handlers.
  - `app/repositories/monetdb_repo.py`: Parameterized SQL queries isolating columnar queries from route handlers.
- **Health Probes**:
  - Liveness probe: `GET /health` and `GET /api/v1/health` (process responsiveness).
  - Readiness probe: `GET /ready` and `GET /api/v1/ready` (validates independent Neo4j & MonetDB connectivity without leaking credentials).
- **Role**:
  - Serves as the middle tier abstracting database complexities.
  - Exposes `/api/v1/recommendations` querying Neo4j (Phase 3.2+).
  - Exposes `/api/v1/analytics` querying MonetDB (Phase 3.2+).
  - Exposes benchmarking metrics comparing query runtimes.

### 3.3 Graph Database (Neo4j Community Edition)
- **Version**: `5.26.0` (Containerized).
- **Storage**: Persistent Docker volume (`cinegraph_neo4j_data`).
- **Use Cases**:
  - Collaborative filtering (Users who rated X also rated Y).
  - Degree of separation / Co-acting networks.
  - Genre-based graph traversals.

### 3.4 Analytical Database (MonetDB)
- **Version**: Official `monetdb/monetdb` (Containerized).
- **Storage**: Persistent Docker volume (`cinegraph_monetdb_data`).
- **Use Cases**:
  - Computing average rating per genre per release decade.
  - High-throughput aggregation of millions of user ratings.
  - Comparative benchmark queries against row-based and graph-based aggregations.

### 3.5 Ingestion Pipeline (Implemented in Phase 2)
- Ingests raw MovieLens 32M datasets (`movies.csv`, `ratings.csv`, `tags.csv`, `links.csv`).
- Sanitizes and structures data for streaming dual ingestion:
  - Generates parameterized, idempotent batch Cypher queries for Neo4j (`MERGE`).
  - Executes batch parameterized SQL inserts for MonetDB relational tables (`INSERT INTO ...`).
- Supports preflight schema validation, small-sample mode, and idempotency across repeated runs.

---

## 4. Current Implementation Status vs. Planned Roadmap

| Component | Status | Details |
|---|---|---|
| **Repository Structure** | Implemented | Monorepo layout with `frontend`, `backend`, `docker`, `docs` |
| **FastAPI Skeleton** | Implemented | Health endpoint (`GET /health`), Root info endpoint (`GET /`), typed configuration |
| **Backend Foundation & DB Access** | Implemented (Phase 3.1) | `DatabaseManager`, Neo4jRepository, MonetDBRepository, `/ready` probe, custom exception hierarchy |
| **Frontend Foundation** | Implemented | Next.js App Router with TypeScript & Tailwind CSS, clean CineGraph hero layout |
| **Docker Compose** | Implemented | Orchestrates Neo4j Community & MonetDB with persisted volumes and port bindings |
| **Database Adapters** | Implemented | Python drivers (`neo4j` and `pymonetdb`) connection integration verified |
| **MovieLens ETL** | Implemented | Streaming, idempotent dual-database ingestion pipeline with preflight and sample modes |
| **Integrity Verification** | Implemented | Automated verification checking counts, foreign keys, and sample queries |
| **Analytics Dashboard** | Planned | Recharts / Chart.js integration displaying MonetDB aggregated stats |
| **Recommendation Engine**| Planned | Cypher graph queries and personalized recommendation endpoints |
| **Performance Benchmark**| Planned | Execution-time comparative evaluation framework |

