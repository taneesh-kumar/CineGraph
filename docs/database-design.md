# CineGraph Database Design & Data Modeling (Phase 2 Final)

This document specifies the shared data models for **Neo4j** (Graph Database) and **MonetDB** (Column-Store Analytical Database), designed for the **MovieLens 32M** dataset.

---

## 1. Dual-Database Paradigm Rationale

| Dimension | Neo4j (Graph Database) | MonetDB (Columnar Database) |
|---|---|---|
| **Primary Focus** | Deep relational traversals, entity connectivity, personalized recommendations | High-throughput columnar aggregation, filtering across millions of records |
| **Query Language** | Cypher | SQL |
| **Optimized For** | Variable-length paths, collaborative filtering, graph centrality | `AVG()`, `COUNT()`, `GROUP BY`, percentile statistics across release years and genres |
| **Storage Structure** | Property Graph (Nodes & Directed Relationships with Properties) | Normalized Relational Columnar Store (Values stored contiguously by column) |
| **Typical Operation** | "Find movies recommended to User 42 based on users with similar rating patterns" | "Calculate average rating trend per genre between 1990 and 2024 across 32M ratings" |

---

## 2. Shared Identity Rules

To ensure academic rigor and coherent cross-engine querying:
1. **Source Identifiers**: The MovieLens `movieId` and `userId` integer keys are strictly preserved and identical in both databases.
2. **Deterministic Genres**: Genre names (e.g. `Action`, `Sci-Fi`, `Drama`) match identically between Neo4j `(:Genre {name: ...})` nodes and MonetDB `genres.name` column.
3. **External Identifiers**: `imdbId` and `tmdbId` are preserved as string identifiers in both databases, differentiating missing values (`NULL`) from valid IDs.
4. **No Cast/Crew Fabrication**: MovieLens 32M does not include cast/director CSVs in this release; hence no fictitious Person/Actor nodes are generated.

---

## 3. Neo4j Graph Model

### 3.1 Nodes (Labels & Key Properties)

- **`:Movie`**
  - `movieId: Int` (Unique Constraint)
  - `title: String`
  - `year: Int` (or `null`)
  - `imdbId: String` (or `null`)
  - `tmdbId: String` (or `null`)

- **`:Genre`**
  - `name: String` (Unique Constraint, e.g., "Action", "Sci-Fi", "Comedy")

- **`:User`**
  - `userId: Int` (Unique Constraint)

### 3.2 Relationships (Edges & Properties)

- `(Movie)-[:IN_GENRE]->(Genre)`
- `(User)-[:RATED { rating: Float, timestamp: Int }]->(Movie)`
- `(User)-[:TAGGED { tag: String, timestamp: Int }]->(Movie)`

### 3.3 Constraints & Indexes

```cypher
CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.movieId IS UNIQUE;
CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE;
CREATE CONSTRAINT genre_name_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE;
CREATE INDEX movie_title_idx IF NOT EXISTS FOR (m:Movie) ON (m.title);
```

---

## 4. MonetDB Analytical Schema

MonetDB stores normalized columnar tables for ultra-fast aggregation over ratings and metadata.

### 4.1 Table Definitions

```sql
-- Movies Table
CREATE TABLE IF NOT EXISTS movies (
    movie_id INT,
    title VARCHAR(512) NOT NULL,
    release_year SMALLINT,
    PRIMARY KEY (movie_id)
);

-- Genres Table
CREATE TABLE IF NOT EXISTS genres (
    genre_id INT,
    name VARCHAR(64) NOT NULL UNIQUE,
    PRIMARY KEY (genre_id)
);

-- Movie Genres Junction Table
CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- Movie External Identifiers Table
CREATE TABLE IF NOT EXISTS movie_links (
    movie_id INT,
    imdb_id VARCHAR(32),
    tmdb_id VARCHAR(32),
    PRIMARY KEY (movie_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

-- Users Dimension Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT,
    PRIMARY KEY (user_id)
);

-- Ratings Fact Table (Massive Columnar Table)
CREATE TABLE IF NOT EXISTS ratings (
    user_id INT,
    movie_id INT,
    rating DECIMAL(2,1) NOT NULL,
    rated_at TIMESTAMP,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

-- Tags Fact Table
CREATE TABLE IF NOT EXISTS tags (
    user_id INT,
    movie_id INT,
    tag VARCHAR(512) NOT NULL,
    tagged_at TIMESTAMP
);
```

---

## 5. Typical Analytical & Benchmark Queries

### 5.1 MonetDB Aggregation: Genre Rating Trends Over Decades
```sql
SELECT 
    g.name AS genre,
    (m.release_year / 10) * 10 AS decade,
    COUNT(r.rating) AS total_ratings,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM ratings r
JOIN movies m ON r.movie_id = m.movie_id
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
WHERE m.release_year IS NOT NULL
GROUP BY genre, decade
ORDER BY decade DESC, avg_rating DESC;
```

### 5.2 Neo4j Collaborative Traversal: Users with Similar Taste
```cypher
MATCH (u1:User {userId: $target_user})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User)
WHERE abs(r1.rating - r2.rating) <= 0.5 AND u1 <> u2
WITH u2, count(m) AS common_movies
WHERE common_movies >= 5
MATCH (u2)-[r3:RATED]->(rec:Movie)
WHERE NOT (u1)-[:RATED]->(rec) AND r3.rating >= 4.0
RETURN rec.title AS recommended_movie, count(u2) AS recommendation_strength
ORDER BY recommendation_strength DESC
LIMIT 10;
```
