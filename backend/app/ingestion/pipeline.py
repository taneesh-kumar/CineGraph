import csv
import logging
import os
from typing import Dict, Generator, List, Optional, Set, Tuple
from app.ingestion.dataset_validator import DatasetValidator
from app.ingestion.transformers import Transformers
from app.ingestion.neo4j_loader import Neo4jLoader
from app.ingestion.monetdb_loader import MonetDBLoader

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Coordinates end-to-end ingestion from raw MovieLens CSV files
    into both Neo4j (graph) and MonetDB (columnar SQL).
    """

    def __init__(
        self,
        dataset_dir: str,
        neo4j_loader: Neo4jLoader,
        monetdb_loader: MonetDBLoader,
        batch_size: int = 5000,
        sample_limit: int = 0,
    ):
        self.dataset_dir = dataset_dir
        self.neo4j = neo4j_loader
        self.monetdb = monetdb_loader
        self.batch_size = batch_size
        self.sample_limit = sample_limit
        self.validator = DatasetValidator(dataset_dir)
        self.metrics: Dict[str, Dict[str, int]] = {
            "movies": {"read": 0, "loaded": 0, "skipped": 0},
            "genres": {"loaded": 0},
            "links": {"read": 0, "loaded": 0, "skipped": 0},
            "ratings": {"read": 0, "loaded": 0, "skipped": 0},
            "tags": {"read": 0, "loaded": 0, "skipped": 0},
        }

    def run_preflight_checks(self):
        """Validate files and headers before ingestion starts."""
        self.validator.validate_files_exist()
        self.validator.validate_headers()
        logger.info("Dataset preflight checks passed successfully.")

    def setup_database_schemas(self):
        """Ensure constraints in Neo4j and tables in MonetDB."""
        self.neo4j.setup_constraints()
        self.monetdb.setup_schema()
        logger.info("Database schemas and constraints initialized.")

    def ingest_movies_and_genres(self) -> Set[int]:
        """
        Ingest movies and genres into both Neo4j and MonetDB.
        Returns the set of ingested movie IDs (used for consistent referential filtering in sample mode).
        """
        movies_csv = os.path.join(self.dataset_dir, "movies.csv")
        ingested_movie_ids: Set[int] = set()
        all_unique_genres: Set[str] = set()

        neo4j_movie_batch = []
        monetdb_movie_batch = []
        monetdb_movie_genres_batch = []

        # Read genres and movies in streaming batches
        with open(movies_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_id = Transformers.sanitize_id(row.get("movieId", ""))
                raw_title = row.get("title", "")
                if movie_id is None or not raw_title:
                    self.metrics["movies"]["skipped"] += 1
                    continue

                self.metrics["movies"]["read"] += 1
                clean_title, release_year = Transformers.extract_year_and_title(raw_title)
                genres = Transformers.parse_genres(row.get("genres", ""))
                for g in genres:
                    all_unique_genres.add(g)

                ingested_movie_ids.add(movie_id)

                neo4j_movie_batch.append({
                    "movieId": movie_id,
                    "title": clean_title,
                    "year": release_year,
                    "imdbId": None,
                    "tmdbId": None,
                    "genres": genres,
                })
                monetdb_movie_batch.append((movie_id, clean_title, release_year))

                # Flush batch
                if len(neo4j_movie_batch) >= self.batch_size:
                    self._flush_movies_batch(
                        neo4j_movie_batch,
                        monetdb_movie_batch,
                        all_unique_genres,
                    )
                    neo4j_movie_batch.clear()
                    monetdb_movie_batch.clear()

                if self.sample_limit > 0 and len(ingested_movie_ids) >= self.sample_limit:
                    logger.info(f"Sample limit reached: {self.sample_limit} movies selected.")
                    break

        # Flush remaining
        if neo4j_movie_batch:
            self._flush_movies_batch(
                neo4j_movie_batch,
                monetdb_movie_batch,
                all_unique_genres,
            )

        self.metrics["genres"]["loaded"] = len(all_unique_genres)
        self.metrics["movies"]["loaded"] = len(ingested_movie_ids)
        logger.info(f"Movies ingested: {len(ingested_movie_ids)} | Unique genres: {len(all_unique_genres)}")
        return ingested_movie_ids

    def _flush_movies_batch(self, neo4j_batch, monetdb_batch, all_genres):
        """Internal helper to load unique genres and movie batches."""
        genre_list = list(all_genres)
        self.neo4j.load_genres(genre_list)
        self.monetdb.load_genres(genre_list)
        genre_map = self.monetdb.get_genre_map()

        # Build movie_genres tuples for MonetDB
        movie_genres_tuples = []
        for item in neo4j_batch:
            mid = item["movieId"]
            for g in item["genres"]:
                if g in genre_map:
                    movie_genres_tuples.append((mid, genre_map[g]))

        self.neo4j.load_movies_batch(neo4j_batch)
        self.monetdb.load_movies_batch(monetdb_batch, movie_genres_tuples)

    def ingest_links(self, valid_movie_ids: Set[int]):
        """Ingest external IMDb and TMDb IDs from links.csv."""
        links_csv = os.path.join(self.dataset_dir, "links.csv")
        neo4j_batch = []
        monetdb_batch = []

        with open(links_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_id = Transformers.sanitize_id(row.get("movieId", ""))
                if movie_id is None or movie_id not in valid_movie_ids:
                    self.metrics["links"]["skipped"] += 1
                    continue

                self.metrics["links"]["read"] += 1
                imdb_id = Transformers.sanitize_str(row.get("imdbId"))
                tmdb_id = Transformers.sanitize_str(row.get("tmdbId"))

                neo4j_batch.append({"movieId": movie_id, "imdbId": imdb_id, "tmdbId": tmdb_id})
                monetdb_batch.append((movie_id, imdb_id, tmdb_id))

                if len(neo4j_batch) >= self.batch_size:
                    self.neo4j.load_links_batch(neo4j_batch)
                    self.monetdb.load_links_batch(monetdb_batch)
                    self.metrics["links"]["loaded"] += len(neo4j_batch)
                    neo4j_batch.clear()
                    monetdb_batch.clear()

        if neo4j_batch:
            self.neo4j.load_links_batch(neo4j_batch)
            self.monetdb.load_links_batch(monetdb_batch)
            self.metrics["links"]["loaded"] += len(neo4j_batch)

        logger.info(f"Links loaded: {self.metrics['links']['loaded']}")

    def ingest_ratings(self, valid_movie_ids: Set[int]) -> Set[int]:
        """
        Stream and ingest ratings into Neo4j and MonetDB.
        Returns the set of user IDs that were referenced and loaded.
        """
        ratings_csv = os.path.join(self.dataset_dir, "ratings.csv")
        ingested_user_ids: Set[int] = set()

        neo4j_batch = []
        monetdb_batch = []
        user_batch = set()

        with open(ratings_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_id = Transformers.sanitize_id(row.get("movieId", ""))
                user_id = Transformers.sanitize_id(row.get("userId", ""))
                rating = Transformers.sanitize_float(row.get("rating", ""))
                ts_int = Transformers.sanitize_id(row.get("timestamp", ""))

                if movie_id is None or user_id is None or rating is None or movie_id not in valid_movie_ids:
                    self.metrics["ratings"]["skipped"] += 1
                    continue

                # Ensure rating is in valid MovieLens range [0.5, 5.0]
                if rating < 0.5 or rating > 5.0:
                    self.metrics["ratings"]["skipped"] += 1
                    continue

                self.metrics["ratings"]["read"] += 1
                ingested_user_ids.add(user_id)
                user_batch.add(user_id)
                rated_at_dt = Transformers.parse_timestamp(str(ts_int)) if ts_int else None

                neo4j_batch.append({
                    "userId": user_id,
                    "movieId": movie_id,
                    "rating": rating,
                    "timestamp": ts_int or 0,
                })
                monetdb_batch.append((user_id, movie_id, rating, rated_at_dt))

                if len(neo4j_batch) >= self.batch_size:
                    # Ingest user nodes first for MonetDB foreign keys
                    self.monetdb.load_users_batch(list(user_batch))
                    self.neo4j.load_ratings_batch(neo4j_batch)
                    self.monetdb.load_ratings_batch(monetdb_batch)
                    self.metrics["ratings"]["loaded"] += len(neo4j_batch)
                    neo4j_batch.clear()
                    monetdb_batch.clear()
                    user_batch.clear()

                # If sample limit is active, limit ratings proportionally (e.g. 50x movie limit)
                if self.sample_limit > 0 and self.metrics["ratings"]["loaded"] >= self.sample_limit * 50:
                    break

        if neo4j_batch:
            self.monetdb.load_users_batch(list(user_batch))
            self.neo4j.load_ratings_batch(neo4j_batch)
            self.monetdb.load_ratings_batch(monetdb_batch)
            self.metrics["ratings"]["loaded"] += len(neo4j_batch)

        logger.info(f"Ratings loaded: {self.metrics['ratings']['loaded']} from {len(ingested_user_ids)} users.")
        return ingested_user_ids

    def ingest_tags(self, valid_movie_ids: Set[int], valid_user_ids: Set[int]):
        """Stream and ingest user tags."""
        tags_csv = os.path.join(self.dataset_dir, "tags.csv")
        neo4j_batch = []
        monetdb_batch = []
        user_batch = set()

        with open(tags_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_id = Transformers.sanitize_id(row.get("movieId", ""))
                user_id = Transformers.sanitize_id(row.get("userId", ""))
                tag = Transformers.sanitize_str(row.get("tag", ""))
                ts_int = Transformers.sanitize_id(row.get("timestamp", ""))

                if movie_id is None or user_id is None or not tag or movie_id not in valid_movie_ids:
                    self.metrics["tags"]["skipped"] += 1
                    continue

                self.metrics["tags"]["read"] += 1
                user_batch.add(user_id)
                tagged_at_dt = Transformers.parse_timestamp(str(ts_int)) if ts_int else None

                neo4j_batch.append({
                    "userId": user_id,
                    "movieId": movie_id,
                    "tag": tag,
                    "timestamp": ts_int or 0,
                })
                monetdb_batch.append((user_id, movie_id, tag, tagged_at_dt))

                if len(neo4j_batch) >= self.batch_size:
                    self.monetdb.load_users_batch(list(user_batch))
                    self.neo4j.load_tags_batch(neo4j_batch)
                    self.monetdb.load_tags_batch(monetdb_batch)
                    self.metrics["tags"]["loaded"] += len(neo4j_batch)
                    neo4j_batch.clear()
                    monetdb_batch.clear()
                    user_batch.clear()

                if self.sample_limit > 0 and self.metrics["tags"]["loaded"] >= self.sample_limit * 10:
                    break

        if neo4j_batch:
            self.monetdb.load_users_batch(list(user_batch))
            self.neo4j.load_tags_batch(neo4j_batch)
            self.monetdb.load_tags_batch(monetdb_batch)
            self.metrics["tags"]["loaded"] += len(neo4j_batch)

        logger.info(f"Tags loaded: {self.metrics['tags']['loaded']}")

    def run(self) -> Dict:
        """Execute full pipeline workflow."""
        logger.info("Starting CineGraph Ingestion Pipeline...")
        self.run_preflight_checks()
        self.setup_database_schemas()

        logger.info("Step 1/4: Ingesting Movies and Genres...")
        valid_movie_ids = self.ingest_movies_and_genres()

        logger.info("Step 2/4: Ingesting Links (IMDb & TMDb IDs)...")
        self.ingest_links(valid_movie_ids)

        logger.info("Step 3/4: Ingesting Ratings...")
        valid_user_ids = self.ingest_ratings(valid_movie_ids)

        logger.info("Step 4/4: Ingesting Tags...")
        self.ingest_tags(valid_movie_ids, valid_user_ids)

        logger.info("Ingestion complete. Collecting final counts...")
        neo4j_counts = self.neo4j.count_entities()
        monetdb_counts = self.monetdb.count_table_rows()

        return {
            "metrics": self.metrics,
            "neo4j_counts": neo4j_counts,
            "monetdb_counts": monetdb_counts,
        }
