# CineGraph REST API Reference

The CineGraph backend exposes REST endpoints under the `/api/v1` versioned prefix, with interactive OpenAPI Swagger UI available at `/docs`.

## Base URL & Interactive Docs
- **Base URL**: `http://127.0.0.1:8000`
- **OpenAPI / Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 1. System Health & Probes

### 1.1 Liveness Probe
- **Endpoint**: `GET /health` or `GET /api/v1/health`
- **Description**: Confirms the FastAPI server process is online.
- **Response**: `200 OK`
```json
{
  "status": "ok",
  "service": "CineGraph API",
  "version": "0.2.0"
}
```

### 1.2 Database Readiness Probe
- **Endpoint**: `GET /ready` or `GET /api/v1/ready`
- **Description**: Checks live TCP connectivity to Neo4j (Bolt 7687) and MonetDB (MAPI 50000). Returns 503 if any database is offline without leaking passwords or stack traces.
- **Response**: `200 OK` (or `503 Service Unavailable`)
```json
{
  "status": "ready",
  "neo4j": {
    "status": "connected",
    "details": null
  },
  "monetdb": {
    "status": "connected",
    "details": null
  }
}
```

---

## 2. Movie Discovery & Search Endpoints

### 2.1 Search Movies by Title Substring
- **Endpoint**: `GET /api/v1/movies/search`
- **Query Parameters**:
  - `q` (string, optional, default: `""`): Substring to match in movie titles (case-insensitive).
  - `limit` (int, optional, default: 20, min: 1, max: 100): Maximum results to return.
- **Response**: `200 OK`
```json
[
  {
    "movie_id": 1,
    "title": "Toy Story (1995)",
    "year": 1995,
    "genres": ["Adventure", "Animation", "Children", "Comedy", "Fantasy"],
    "imdb_id": "0114709",
    "tmdb_id": "862"
  }
]
```

### 2.2 Get Movie by ID
- **Endpoint**: `GET /api/v1/movies/{movie_id}`
- **Response**: `200 OK`
```json
{
  "movie_id": 1,
  "title": "Toy Story (1995)",
  "year": 1995,
  "genres": ["Adventure", "Animation", "Children", "Comedy", "Fantasy"],
  "imdb_id": "0114709",
  "tmdb_id": "862"
}
```
- **Error Statuses**:
  - `404 Not Found`: Movie ID does not exist in the dataset.
  - `422 Unprocessable Entity`: `movie_id < 1`.

### 2.3 List Sample Movies
- **Endpoint**: `GET /api/v1/movies`
- **Query Parameters**:
  - `limit` (int, default: 20, min: 1, max: 100): Maximum results to return.
- **Response**: `200 OK` (Array of `MovieSummary`)

---

## 3. Graph Recommendation Endpoints (Neo4j)

### 2.1 Similar Movies by MovieLens ID
- **Endpoint**: `GET /api/v1/recommendations/movie/{movie_id}`
- **Query Parameters**:
  - `limit` (int, default: 10, min: 1, max: 50): Number of recommendations to return.
- **Behavior**: Ranks candidates sharing genres and rating evidence with the source movie. The source movie is strictly excluded.
- **Response**: `200 OK`
```json
{
  "source_type": "movie",
  "source_id": 1,
  "source_title": "Toy Story (1995)",
  "recommendations": [
    {
      "movie_id": 3114,
      "title": "Toy Story 2 (1999)",
      "year": 1999,
      "genres": ["Adventure", "Animation", "Children", "Comedy", "Fantasy"],
      "score": 8.05,
      "explanation": "Shares 3 genre(s) (Adventure, Animation, Children) with 'Toy Story (1995)' with an average rating of 4.1/5.0",
      "imdb_id": "0120363",
      "tmdb_id": "863"
    }
  ],
  "total_found": 1
}
```
- **Error Statuses**:
  - `404 Not Found`: Movie ID does not exist in the database.
  - `422 Unprocessable Entity`: `movie_id < 1` or `limit` out of range.

### 2.2 Personalized Recommendations by User ID
- **Endpoint**: `GET /api/v1/recommendations/user/{user_id}`
- **Query Parameters**:
  - `limit` (int, default: 10, min: 1, max: 50): Number of recommendations to return.
- **Behavior**: Traverses bipartite rating graph for peers with overlapping high ratings (`>= 3.5`). Automatically filters out all movies already rated by the target user. Falls back to favorite genre expansion when collaborative signals are sparse.
- **Response**: `200 OK`
```json
{
  "source_type": "user",
  "source_id": 1,
  "source_title": "User #1",
  "recommendations": [
    {
      "movie_id": 260,
      "title": "Star Wars: Episode IV - A New Hope (1977)",
      "year": 1977,
      "genres": ["Action", "Adventure", "Sci-Fi"],
      "score": 12.8,
      "explanation": "Recommended based on 6 user(s) with similar rating taste who rated this movie an average of 4.3/5.0",
      "imdb_id": "0076759",
      "tmdb_id": "11"
    }
  ],
  "total_found": 1
}
```

---

## 3. Analytical Endpoints (MonetDB)

### 3.1 Top-Rated Movies
- **Endpoint**: `GET /api/v1/analytics/top-rated`
- **Query Parameters**:
  - `min_ratings` (int, default: 10, min: 1, max: 10000): Threshold filter to eliminate low-sample rating bias.
  - `limit` (int, default: 20, min: 1, max: 100): Number of top movies to retrieve.
- **Response**: `200 OK`
```json
[
  {
    "movie_id": 318,
    "title": "Shawshank Redemption, The (1994)",
    "release_year": 1994,
    "avg_rating": 4.41,
    "rating_count": 557,
    "genres": ["Crime", "Drama"]
  }
]
```

### 3.2 Genre Popularity Metrics
- **Endpoint**: `GET /api/v1/analytics/genres`
- **Description**: Columnar aggregation of rating count, distinct movies, and average rating per genre.
- **Response**: `200 OK`
```json
[
  {
    "genre": "Drama",
    "total_ratings": 21698,
    "distinct_movies": 450,
    "avg_rating": 3.7
  },
  {
    "genre": "Comedy",
    "total_ratings": 18192,
    "distinct_movies": 380,
    "avg_rating": 3.42
  }
]
```

### 3.3 Rating Score Distribution
- **Endpoint**: `GET /api/v1/analytics/ratings/distribution`
- **Description**: Frequency counts and percentage shares across discrete MovieLens ratings (`0.5` through `5.0`).
- **Response**: `200 OK`
```json
[
  {
    "rating": 0.5,
    "count": 782,
    "percentage": 1.56
  },
  {
    "rating": 4.0,
    "count": 13410,
    "percentage": 26.82
  }
]
```

### 3.4 Movie Rating Statistics
- **Endpoint**: `GET /api/v1/analytics/movies/{movie_id}/ratings`
- **Description**: Evaluates single-movie rating count and average rating.
- **Response**: `200 OK`
```json
{
  "movie_id": 1,
  "rating_count": 215,
  "avg_rating": 3.92
}
```
- **Error Statuses**:
  - `404 Not Found`: Movie does not exist in the database.

### 3.5 Global Dataset Summary
- **Endpoint**: `GET /api/v1/analytics/summary`
- **Description**: Summary counts across all entities in the database.
- **Response**: `200 OK`
```json
{
  "total_movies": 1000,
  "total_users": 2364,
  "total_genres": 19,
  "total_ratings": 50000,
  "total_tags": 10000
}
```

---

## 4. Local Development Startup
To run the backend server locally:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test any of the above endpoints interactively in your browser.

---

## 5. Performance Baseline & Historical Benchmarks

> **Historical Note**: The following baseline measurements were conducted during Phase 3.4 on the initial 1,000-movie development baseline (1,000 movies, 2,364 users, 19 genres, 50,000 ratings, 10,000 tags) over 10 repeated requests per endpoint:

| Endpoint | Target Engine | Cold Request | Mean Warm | Median Warm | Range (Min - Max) |
|---|---|---|---|---|---|
| `GET /api/v1/health` | Application Process | 1.78 ms | 0.68 ms | 0.67 ms | 0.63 ms – 1.78 ms |
| `GET /api/v1/ready` | Neo4j + MonetDB TCP Probes | 8.39 ms | 6.71 ms | 6.23 ms | 5.35 ms – 9.28 ms |
| `GET /api/v1/recommendations/movie/1?limit=10` | Neo4j Cypher Traversal | 12.30 ms | 15.59 ms | 13.45 ms | 11.43 ms – 28.91 ms |
| `GET /api/v1/recommendations/user/1?limit=10` | Neo4j Collaborative Traversal | 131.80 ms | 134.22 ms | 131.47 ms | 128.60 ms – 149.00 ms |
| `GET /api/v1/analytics/top-rated?min_ratings=20&limit=20` | MonetDB Columnar SQL | 107.07 ms | 111.33 ms | 112.19 ms | 104.51 ms – 116.42 ms |
| `GET /api/v1/analytics/genres` | MonetDB Columnar Aggregation | 15.38 ms | 13.21 ms | 12.99 ms | 11.70 ms – 16.47 ms |
| `GET /api/v1/analytics/ratings/distribution` | MonetDB Group By Aggregation | 6.06 ms | 7.11 ms | 6.49 ms | 5.84 ms – 9.51 ms |
| `GET /api/v1/analytics/movies/1/ratings` | MonetDB Single-Entity Stats | 11.16 ms | 13.15 ms | 13.20 ms | 11.16 ms – 15.03 ms |
| `GET /api/v1/analytics/summary` | MonetDB Global Entity Counts | 7.50 ms | 8.44 ms | 8.51 ms | 7.23 ms – 9.14 ms |

### Key Benchmark Observations:
- **Graph Similarity Performance**: Content and genre-based graph candidate exploration completes in **~13–15 ms** on Neo4j.
- **Collaborative Filtering**: Peer-user collaborative graph traversal runs in **~134 ms** over 50,000 rating relationships without external cache.
- **Columnar Analytical Throughput**: High-throughput aggregations like `ratings/distribution` (**~7 ms**) and `analytics/genres` (**~13 ms**) benefit from MonetDB's contiguous column storage.
- **Network Resolution Optimization**: Binding database connections explicitly to IPv4 `127.0.0.1` avoids Windows hostname lookup penalties.

