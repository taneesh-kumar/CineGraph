# CineGraph Local Development Setup

This guide provides end-to-end instructions for configuring and running the **CineGraph** environment locally on your development machine.

---

## 1. Prerequisites

Before starting, ensure you have the following installed:

- **Git**: Installed and configured.
- **Node.js**: `v20.x` or later (tested on Node `v25.2.1`).
- **npm**: `v10.x` or later (tested on npm `v11.6.2`).
- **Python**: `3.11` or `3.12+` (tested on Python `3.11.9`).
- **Docker Desktop**: Running with Docker Compose support (`v2.x`+).

---

## 2. Environment Configuration

Copy the example environment template in the project root:

```powershell
# In repository root
Copy-Item .env.example .env
```

Review and adjust credentials in `.env` if desired (passwords, ports). **Never commit `.env` to Git.**

---

## 3. Database Infrastructure (Docker)

Both Neo4j and MonetDB are containerized. Do **not** install them natively on Windows.

### 3.1 Start Database Containers
```powershell
docker compose up -d
```

### 3.2 Verify Status
```powershell
docker compose ps
```
You should see `cinegraph-neo4j` and `cinegraph-monetdb` in `Up` (or `healthy`) status.

### 3.3 Access Database Interfaces
- **Neo4j Browser**: Open [http://127.0.0.1:7474](http://127.0.0.1:7474) in your browser.
  - Authentication: User `neo4j`, password from your `.env` (default: `cinegraph_neo4j_secret_change_me`).
  - Bolt URL: `bolt://127.0.0.1:7687`
- **MonetDB MAPI**: Port `127.0.0.1:50000` (managed via `mclient` or `pymonetdb`).

### 3.4 Stopping Containers
```powershell
# Stop containers while preserving data volumes:
docker compose stop
# or
docker compose down
```

---

## 4. Backend Setup & Ingestion Pipeline

### 4.1 Setup Virtual Environment
```powershell
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# (On Linux/macOS: source .venv/bin/activate)
```

### 4.2 Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4.3 Run Test Suite
```powershell
pytest
```

### 4.4 Ingesting MovieLens 32M Data

CineGraph includes a streaming, idempotent data ingestion pipeline that synchronizes `ml-32m` into both databases.

#### Preflight Dataset Validation Only
```powershell
python -m app.ingestion.cli --validate-only
```

#### Running a Development Sample Import (e.g. 1,000 Movies)
```powershell
python -m app.ingestion.cli --sample-limit 1000 --batch-size 1000
```

#### Running Full MovieLens 32M Ingestion
```powershell
python -m app.ingestion.cli --sample-limit 0 --batch-size 5000
```

#### Verifying Database Integrity & Cross-Engine Consistency
```powershell
python -m app.ingestion.verify
```

### 4.5 Start Development Server
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Liveness Probe: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) or `/api/v1/health`
- Database Readiness Probe: [http://127.0.0.1:8000/ready](http://127.0.0.1:8000/ready) or `/api/v1/ready`
- Interactive OpenAPI Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 5. Frontend Setup (Next.js)

### 5.1 Install Dependencies
```powershell
cd frontend
npm install
```

### 5.2 Start Development Server
```powershell
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the CineGraph interface.

### 5.3 Production Build Verification
```powershell
npm run build
```

---

## 6. Port Summary

| Service | Host Port | Protocol / Path | Purpose |
|---|---|---|---|
| **Next.js Frontend** | `3000` | HTTP | CineGraph Web UI |
| **FastAPI Backend** | `8000` | HTTP | CineGraph REST API & Swagger |
| **Neo4j Browser** | `7474` | HTTP | Neo4j UI & Cypher console |
| **Neo4j Bolt** | `7687` | Bolt TCP | Binary driver connection |
| **MonetDB MAPI** | `50000` | MAPI TCP | MonetDB SQL analytical queries |
