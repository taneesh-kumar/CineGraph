# CineGraph — Frontend Architecture & User Interface Documentation

## 1. Overview & Objectives

**CineGraph** features a modern, accessible, dark cinematic frontend built with **Next.js 16 (App Router)** and **React 19**, designed to showcase the practical differences between two complementary NoSQL database engines:

- **Neo4j Community Edition (Graph Database, Bolt Port 7687):** Entity relationships, movie topology, genre associations, Jaccard content similarity, and collaborative community walks.
- **MonetDB (Analytical Column-Store, MAPI Port 50000):** Vectorized scans, rating aggregations, minimum-threshold rankings, and 0.5–5.0 star rating distributions across millions of rating tuples.
- **FastAPI (Application Gateway, Port 8000):** Versioned REST API layer (`/api/v1`) shielding database credentials and enforcing strict Pydantic schemas.

---

## 2. Technology Stack

- **Framework:** Next.js 16.4.2 with Turbopack & Partial Prerendering (PPR).
- **Core Library:** React 19.3.0.
- **Language:** TypeScript 5.
- **Styling:** Tailwind CSS v4 (`@import "tailwindcss"`).
- **Icons:** `lucide-react` (SVG-based, tree-shaken, accessible).
- **Testing:** Node.js Native Test Runner (`node --test`) with `--experimental-strip-types`.
- **API Client:** Type-safe Fetch wrapper (`frontend/lib/api/client.ts`) with custom `ApiError` class.

---

## 3. Application Routes & Navigation

| Route | Name | Primary Engine | Description |
|---|---|---|---|
| `/` | **Overview** | Hybrid (Neo4j + MonetDB) | System summary cards, dual-engine architectural breakdown, live readiness status, top-rated preview, and genre preview. |
| `/movies` | **Movie Explorer** | Neo4j | Title search with 350ms debouncing, genre filtering chips, responsive movie cards with ID, year, and rating indicators. |
| `/movies/[movieId]` | **Movie Details** | Hybrid | Detailed movie metadata, MonetDB rating statistics (avg rating, count, min/max), and Neo4j similar movie graph traversal. |
| `/recommendations` | **Recommendations** | Neo4j | Mode A (Item Jaccard content similarity) and Mode B (User collaborative filtering community walks) with transparent explanations. |
| `/analytics` | **Analytics Dashboard** | MonetDB | Dataset catalog metrics, top-rated movies with interactive rating threshold filters, genre popularity bar chart + data table, and rating distribution histogram. |
| `/system` | **System Status** | FastAPI + Neo4j + MonetDB | Live liveness and readiness diagnostic probes, roundtrip latency metrics, connection status indicators, and architecture notes. |

---

## 4. Component Architecture

```
frontend/
├── app/
│   ├── layout.tsx                 # Root layout with AppShell wrapper
│   ├── page.tsx                   # Overview landing page
│   ├── movies/
│   │   ├── page.tsx               # Movie explorer & debounced search
│   │   └── [movieId]/page.tsx     # Dynamic movie details & similar movies
│   ├── recommendations/
│   │   └── page.tsx               # Item and user recommendations interface
│   ├── analytics/
│   │   └── page.tsx               # Columnar analytics dashboard & charts
│   └── system/
│       └── page.tsx               # Live health, readiness, and latency probes
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx           # Responsive shell with main content container
│   │   ├── Navbar.tsx             # Sticky navigation with mobile menu & active pills
│   │   └── Footer.tsx             # Engine attribution, tech stack, and disclosures
│   ├── movies/
│   │   ├── MovieCard.tsx          # Movie item card with genres, year, and action links
│   │   ├── MovieGrid.tsx          # Responsive 1/2/3/4-column card grid
│   │   └── MovieSearch.tsx        # Debounced input with clear button and sample chips
│   └── ui/
│       ├── EngineBadge.tsx        # Visual badge attributing feature to Neo4j/MonetDB/FastAPI
│       ├── StatCard.tsx           # Metric stat container with subtitle and icon
│       ├── LoadingState.tsx       # Accessible loading spinner with ARIA role
│       ├── ErrorState.tsx         # User-friendly error message container with retry action
│       └── EmptyState.tsx         # Clean container for empty search or query results
├── lib/
│   ├── api/
│   │   └── client.ts              # Typed REST client with error handling & base URL
│   └── types/
│       └── index.ts               # Complete TypeScript interfaces matching backend models
└── tests/
    └── client.test.mjs            # Automated unit and contract integration tests
```

---

## 5. Environment Configuration

The frontend communicates with the FastAPI backend through the environment variable `NEXT_PUBLIC_API_URL`.

Create `frontend/.env.local` (or configure your shell):

```env
# Frontend API Target (Defaults to IPv4 loopback for minimal latency)
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

> **Note:** Use `http://127.0.0.1:8000` rather than `http://localhost:8000` on Windows systems to bypass the ~2-second IPv6 resolution timeout.

---

## 6. Development & Verification Commands

### Prerequisites
Ensure the databases and backend are running:
```bash
# 1. Start Docker containers (Neo4j on 7687, MonetDB on 50000)
docker compose up -d

# 2. Start FastAPI backend
cd backend
.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend Commands
```bash
cd frontend

# Install dependencies
npm install

# Start development server on port 3000
npm run dev

# Run automated frontend unit tests
npm test

# Run ESLint validation
npm run lint

# Build optimized production bundle
npm run build

# Start production server
npm run start
```

---

## 7. Known Dataset Sample Scope

The active environment contains an ingested 2020–2023 subset of MovieLens 32M:
- **2,500 Movies** (Released between 2020 and 2021 within the 2020–2023 query window).
- **18,327 Users** in MonetDB (`movie_users`), **16,224 Active Users** in Neo4j.
- **16 Movie Genres** (with 4,027 movie-genre relationship links).
- **119,689 Ratings** (Average ratings calculated via MonetDB columnar scans).
- **25,999 Tags** in MonetDB, **26,000 Tag Relationships** in Neo4j.

Searches and recommendations outside the 2,500-movie dataset sample gracefully display clear empty states explaining that the target entity was not ingested into the development slice.
