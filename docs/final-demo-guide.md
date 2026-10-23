# CineGraph — Final Academic Demonstration Guide

This guide provides a structured, live demonstration sequence for presenting CineGraph. It highlights **what the system does** and **why Neo4j and MonetDB are suited for their complementary workloads**.

---

## 1. Problem Statement & Motivation (1 Minute)

- **The Challenge**: Modern content platforms require both complex relationship-driven discovery (personalized graph traversals) and high-speed statistical aggregations across millions of interactions.
- **The Pitfall of Single-Paradigm Databases**:
  - Relational row stores slow down on deep recursive graph joins.
  - Native graph databases slow down when computing full columnar aggregations (e.g. scanning hundreds of thousands of rating tuples to calculate percentile distributions).
- **The CineGraph Solution**: A specialized dual-database architecture uniting **Neo4j** (graph pointer chasing) and **MonetDB** (vectorized columnar analytics) behind a unified **FastAPI** service and **Next.js** UI.

---

## 2. System Architecture & Dual-Engine Roles (1 Minute)

Show the architectural flow:
- **Client**: Next.js 16 UI with dark cinematic design.
- **Middleware**: FastAPI with typed Pydantic contracts and independent connection pooling.
- **Neo4j Engine**: Connected via Bolt protocol (Port 7687). Handles graph topology, movie nodes, genre edges, and collaborative peer walks.
- **MonetDB Engine**: Connected via MAPI protocol (Port 50000). Handles columnar fact scans across 119,689 rating tuples and 25,999 tags.

---

## 3. Live Demonstration Sequence

### Step 1: System Health & Diagnostics
- **Target Page**: [http://localhost:3000/system](http://localhost:3000/system)
- **Key Points**:
  - Demonstrate independent readiness probes (`/ready`).
  - Point out real-time connection status to Neo4j (Bolt) and MonetDB (MAPI).
  - Note the active dataset scope: **2,500 movies (2020–2023)**, **18,327 users**, **119,689 ratings**, **16 genres**.

### Step 2: Movie Discovery & Graph Search
- **Target Page**: [http://localhost:3000/movies](http://localhost:3000/movies)
- **Actions**:
  - Click the quick search chip: **Tenet**.
  - Show instantaneous substring search and genre badges (`Action`, `Thriller`).
  - Click on **Tenet** to open the detail view at `/movies/217465`.
  - Highlight the external IMDb and TMDb links, release year (2020), and dual-engine data composition (Neo4j metadata + MonetDB aggregate ratings: 4,332 ratings, 3.6 avg).

### Step 3: Graph Recommendations (Neo4j Engine)
- **Target Page**: [http://localhost:3000/recommendations](http://localhost:3000/recommendations)
- **Similar Movie Recommendations**:
  - Target: Movie ID `217465` (*Tenet*).
  - Point out explainable graph scores: shows shared genre count weighted by rating evidence (e.g. *Ayyappanum Koshiyum* sharing `Action` and `Thriller` with score 6.04).
  - Emphasize source movie exclusion (Tenet never recommends itself).
- **Personalized Collaborative Filtering**:
  - Switch to **User Recommendations** tab.
  - Select active user chip **User #57304 (368 ratings)**.
  - Demonstrate peer community walk: discovers peers with overlapping likes ($\ge 3.5$) and scores candidate movies based on consensus.
  - Verify that already-rated movies are strictly excluded.

### Step 4: Columnar Analytics Dashboard (MonetDB Engine)
- **Target Page**: [http://localhost:3000/analytics](http://localhost:3000/analytics)
- **Key Points**:
  - **Dataset Statistics**: Ingested count cards evaluated via single columnar queries.
  - **Top-Rated Movies**: Demonstrates minimum rating count threshold filter (`min_ratings=20`) to eliminate single-rating skew. Top film: *James Acaster: Cold Lasagne Hate Myself 1999* (4.3★).
  - **Genre Popularity Bar Chart**: Vector scan grouping by genre. Shows *Drama* (42,765 ratings) and *Action* (36,859 ratings) dominating volume.
  - **Rating Distribution Histogram**: Evaluates discrete buckets (`0.5` through `5.0`) summing exactly to 100%, with peak rating at 4.0★.

---

## 4. Benchmark & Recommendation Evaluation Evidence (2 Minutes)

Present the experimental findings from Phase 5:

1. **Query Latency Comparison**:
   - Single Entity Lookup: Neo4j **1.94 ms** vs MonetDB **5.71 ms**.
   - Immediate Genre Lookup: Neo4j **1.90 ms** vs MonetDB **4.18 ms**.
   - Columnar Fact Aggregations: MonetDB calculates rating distributions and top-rated rankings across 119,000+ ratings in **~5 ms**.
   - Collaborative Traversal: Multi-hop graph walk across 16,000+ raters takes **~645 ms** in Neo4j without external cache.
2. **Recommendation Ranking Metrics (Offline Temporal Split)**:
   - Evaluated without future-rating leakage on held-out test ratings ($\ge 4.0$).
   - Precision@5: **14.55%** (CineGraph Collaborative) vs **11.82%** (Global Popularity).
   - Hit Rate@10: **63.64%**.
3. **Concurrency Scaling**:
   - Tested under 1, 2, 5, 10 concurrent clients.
   - Peak throughput achieved at **82.36 req/s** with p95 latency under 185 ms.

---

## 5. Offline Fallback Procedures

If Docker database containers cannot be started during the presentation:
1. **Fallback Data**: Stored benchmark outputs and figures are persisted in `reports/phase-5/` and can be displayed statically:
   - `reports/phase-5/figures/query-latency.png`
   - `reports/phase-5/figures/latency-percentiles.png`
   - `reports/phase-5/figures/concurrency-throughput.png`
   - `reports/phase-5/figures/recommendation-metrics.png`
2. **Automated Smoke Test Verification**:
   - Run `python scripts/smoke_test.py` in terminal to demonstrate live API contract compliance.
