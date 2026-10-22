# CineGraph Backend

The CineGraph backend is built with **FastAPI**, **Pydantic v2**, and asynchronous Python.

## Responsibilities

- Exposes RESTful endpoints for movie exploration, graph traversal, and analytical queries.
- Coordinates between Neo4j (graph recommendations) and MonetDB (analytical aggregations).
- Isolates database credentials and direct drivers from the frontend.

## Prerequisites

- Python 3.11+ (Python 3.12 or 3.13 recommended; tested with 3.11.9 / 3.12)
- Virtual environment tool (`venv`)

## Getting Started

### 1. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Run Test Suite
```bash
pytest
```
