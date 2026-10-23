# CineGraph — Phase 4 Implementation Plan: Complete Frontend & Verification

## 1. Executive Summary & Objective

Phase 4 establishes the complete web application for **CineGraph**, connecting the Next.js 16 (React 19, TypeScript, Tailwind CSS v4) frontend with the existing FastAPI backend, Neo4j graph database, and MonetDB analytical engine.

The frontend highlights the core academic distinction of CineGraph:
- **Neo4j**: Powers movie graph topology, genre relationships, collaborative filtering traversals, and explainable recommendations.
- **MonetDB**: Powers high-throughput columnar aggregations, rating distributions, and genre popularity analytics.
- **FastAPI**: Serves typed REST endpoints under `/api/v1`.
- **Next.js**: Delivers a dark, responsive, accessible cinematic data exploration interface.

---

## 2. Baseline Status & Verified API Contracts

### 2.1 Backend Baseline
- Automated tests: **57 passed in 1.18s**, 0 failed.
- Development database sample: 1,000 movies, 2,364 users, 19 genres, 50,000 ratings, 10,000 tags.
- Verified parity: 100% match between Neo4j and MonetDB entities.

### 2.2 Verified Backend API Endpoints (`/api/v1`)
1. `GET /api/v1/health` — API process liveness probe.
2. `GET /api/v1/ready` — Neo4j and MonetDB readiness verification.
3. `GET /api/v1/recommendations/movie/{movie_id}?limit=N` — Similar movie recommendations with explainability.
4. `GET /api/v1/recommendations/user/{user_id}?limit=N` — Collaborative personalized user recommendations.
5. `GET /api/v1/analytics/top-rated?min_ratings=N&limit=N` — High-rated movies meeting minimum vote threshold.
6. `GET /api/v1/analytics/genres` — Columnar genre rating activity and averages.
7. `GET /api/v1/analytics/ratings/distribution` — Exact rating frequency and percentage shares.
8. `GET /api/v1/analytics/movies/{movie_id}/ratings` — Specific movie rating count and average.
9. `GET /api/v1/analytics/summary` — Global entity counts across movies, users, genres, ratings, tags.

### 2.3 Additional Justified Backend Endpoint
To support Movie Discovery and Search without querying databases directly from the client or loading the whole dataset into browser memory:
- `GET /api/v1/movies/search?q={query}&limit={limit}` — Uses existing repository method `search_movies_by_title`.
- `GET /api/v1/movies/{movie_id}` — Uses existing repository method `get_movie_by_id`.

---

## 3. Frontend Architecture & Page Structure

### 3.1 Routing Structure (`frontend/app/`)
- `/` — Overview landing page with project background, dual-engine metrics, top-rated preview, and genre snapshot.
- `/movies` — Movie explorer with debounced search, genre tags, and quick links to details and recommendations.
- `/movies/[movieId]` — Movie details page combining movie metadata, MonetDB rating statistics, and Neo4j similar-movie recommendations.
- `/recommendations` — Dual-mode recommendation explorer:
  - *Mode A (Similar Movies)*: Enter movie ID or select popular movies to see graph-derived similar titles.
  - *Mode B (Personalized Recommendations)*: Enter user ID (e.g. sample user 1, 42, 100) to see collaborative filtering recommendations with explanations.
- `/analytics` — Analytics dashboard with interactive, accessible charts:
  - Dataset overview stats cards.
  - Top-rated movies table with adjustable minimum rating threshold.
  - Genre popularity chart & accessible table.
  - Rating score distribution chart (0.5 – 5.0).
  - Single-movie rating lookup.
- `/system` — System status page displaying frontend state, backend liveness, Neo4j & MonetDB readiness, and manual refresh controls.

### 3.2 Component Inventory (`frontend/components/`)
- **`layout/`**: `Navbar`, `Footer`, `MobileNav`, `AppShell`, `PageContainer`
- **`ui/`**: `Badge`, `Card`, `Button`, `StatCard`, `Skeleton`, `EmptyState`, `ErrorState`, `EngineBadge`
- **`movies/`**: `MovieCard`, `MovieGrid`, `MovieSearchInput`, `RatingBadge`
- **`recommendations/`**: `RecommendationCard`, `SimilarMoviesSection`, `UserRecommendationsSection`
- **`analytics/`**: `TopRatedTable`, `GenrePopularityChart`, `RatingDistributionChart`, `SummaryCards`
- **`system/`**: `StatusCard`, `DatabaseIndicator`

### 3.3 State & API Client (`frontend/lib/`)
- `lib/api/client.ts` — Centralized, typed API client using `NEXT_PUBLIC_API_URL` (default: `http://127.0.0.1:8000`).
- `lib/types/` — Strict TypeScript interfaces derived directly from backend Pydantic models.

---

## 4. Implementation Checklist

- [x] **Phase 4.0: Discovery & Setup**
  - [x] Inspect existing backend & frontend baselines.
  - [x] Verify API contracts and dependency requirements.
  - [x] Create `docs/phase-4-plan.md`.
- [x] **Phase 4.1: Foundation & Movie Discovery**
  - [x] Implement backend `/api/v1/movies/search` and `/api/v1/movies/{movie_id}` routes with unit tests (5 passing tests).
  - [x] Create TypeScript types matching all backend schemas (`frontend/lib/types/index.ts`).
  - [x] Build typed frontend API client with robust error handling (`frontend/lib/api/client.ts`).
  - [x] Build responsive dark layout (`Navbar`, `Footer`, `AppShell`).
  - [x] Build `/` Overview page with live dataset statistics and quick previews.
  - [x] Build `/movies` Movie Explorer with search, debouncing, and empty/error states.
  - [x] Build `/movies/[movieId]` Movie Details page with metadata, rating stats, and similar recommendations.
- [x] **Phase 4.2: Recommendations & Analytics Dashboard**
  - [x] Build `/recommendations` page with Mode A (Movie-based) and Mode B (User personalized).
  - [x] Build `/analytics` dashboard with dataset summary cards.
  - [x] Build Top-rated movies table with dynamic minimum ratings and limit controls.
  - [x] Build Genre popularity interactive chart & accessible data table.
  - [x] Build Rating distribution chart (0.5 to 5.0) with count & percentage breakdown.
  - [x] Integrate database engine badges (Neo4j vs. MonetDB) indicating data origin.
- [x] **Phase 4.3: System Status, Accessibility, Tests & Final Verification**
  - [x] Build `/system` status page with live probe monitoring and refresh control.
  - [x] Verify responsive layouts across mobile, tablet, and desktop viewports.
  - [x] Ensure accessible semantic HTML, keyboard navigation, and ARIA labels.
  - [x] Add automated frontend tests (`frontend/tests/client.test.mjs` — 11 passing tests).
  - [x] Run full test suites (backend 62 passing tests; frontend 11 passing tests).
  - [x] Verify production Next.js build (`npm run build` completed with code 0).
  - [x] Update documentation (`docs/frontend.md`, `docs/api.md`, `docs/architecture.md`, `README.md`).

---

## 5. Final Verification Results

- **Backend Pytest Suite:** 62 passed in 1.36s (zero failures).
- **Frontend Test Suite:** 11 passed in 36ms (zero failures).
- **ESLint Linting:** Zero errors (`npm run lint` exited with code 0).
- **Production Build:** Next.js 16.4.2 Turbopack optimized build succeeded (`npm run build` exited with code 0).
- **Live API Integration:** All 11 endpoints verified live with HTTP 200 responses.
- **Frontend Route Rendering:** All 6 primary routes (`/`, `/movies`, `/movies/1`, `/recommendations`, `/analytics`, `/system`) verified live with HTTP 200 responses.

