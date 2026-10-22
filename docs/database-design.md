# CineGraph Database Design & Data Modeling

This document outlines the data model for the two core database technologies powering CineGraph: **Neo4j** (Graph Database) and **MonetDB** (Column-Store Analytical Database).

---

## 1. Dual-Database Paradigm Rationale

| Dimension | Neo4j (Graph Database) | MonetDB (Columnar Database) |
|---|---|---|
| **Primary Focus** | Deep relational traversals, entity connectivity, personalized recommendations | High-throughput columnar aggregation, filtering across millions of records |
| **Query Language** | Cypher | SQL |
| **Optimized For** | Variable-length paths, "who acted with whom", graph centrality | `AVG()`, `COUNT()`, `GROUP BY`, percentile statistics across release years and genres |
| **Typical Operation** | "Find 5 movies similar to Interstellar based on director and actor overlap" | "Calculate average rating trend per genre between 1990 and 2020" |

---

## 2. Neo4j Graph Model

### 2.1 Nodes (Labels & Key Properties)

- **`:Movie`**
  - `movieId: Int` (Unique Index)
  - `title: String`
  - `releaseYear: Int`
  - `imdbId: String`
  - `tmdbId: String`

- **`:Person`** (or specialized `:Actor`, `:Director`)
  - `personId: String`
  - `name: String`

- **`:Genre`**
  - `name: String` (Unique Index, e.g., "Action", "Sci-Fi", "Drama")

- **`:User`**
  - `userId: Int` (Unique Index)

### 2.2 Relationships (Edges & Properties)

- `(:Person)-[:ACTED_IN { character: String }]->(:Movie)`
- `(:Person)-[:DIRECTED]->(:Movie)`
- `(:Movie)-[:BELONGS_TO]->(:Genre)`
- `(:User)-[:RATED { rating: Float, timestamp: Int }]->(:Movie)`
- `(:User)-[:TAGGED { tag: String, timestamp: Int }]->(:Movie)`

### 2.3 Key Indexes & Constraints
```cypher
CREATE CONSTRAINT movie_id_unique FOR (m:Movie) REQUIRE m.movieId IS UNIQUE;
CREATE CONSTRAINT user_id_unique FOR (u:User) REQUIRE u.userId IS UNIQUE;
CREATE INDEX genre_name_idx FOR (g:Genre) ON (g.name);
```

---

## 3. MonetDB Analytical Schema

MonetDB stores normalized columnar tables for ultra-fast aggregation over ratings and metadata.

### 3.1 Table Definitions

```sql
-- Movies Table
CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    title VARCHAR(255),
    release_year SMALLINT,
    imdb_id VARCHAR(32),
    tmdb_id VARCHAR(32)
);

-- Genres Table
CREATE TABLE genres (
    genre_id INT PRIMARY KEY,
    name VARCHAR(64) UNIQUE
);

-- Movie Genres Junction Table
CREATE TABLE movie_genres (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

-- Ratings Table (Massive Fact Table)
CREATE TABLE ratings (
    rating_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    movie_id INT,
    rating DECIMAL(2,1),
    rated_at TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

-- Tags Table
CREATE TABLE tags (
    tag_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    movie_id INT,
    tag VARCHAR(255),
    tagged_at TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);
```

### 3.2 Typical Analytical Query Patterns

**Genre Popularity & Average Rating by Decade:**
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
GROUP BY genre, decade
ORDER BY decade DESC, avg_rating DESC;
```

---

## 4. Ingestion Workflow (Planned)

1. **Source Data**: MovieLens CSV datasets (`movies.csv`, `ratings.csv`, `tags.csv`, `links.csv`).
2. **Transform Step**:
   - Clean titles, extract 4-digit release years from title strings.
   - Split pipe-separated genre strings (`Action|Sci-Fi|Thriller`).
3. **Load Step**:
   - Stream into Neo4j via APOC or parameterized Cypher queries.
   - Bulk load into MonetDB via `COPY INTO` for high throughput.
