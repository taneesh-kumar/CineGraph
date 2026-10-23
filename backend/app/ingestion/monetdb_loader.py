import logging
from typing import Dict, List, Optional
import pymonetdb

logger = logging.getLogger(__name__)


class MonetDBLoader:
    """Manages MonetDB schema creation and batch table loading."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """Establish connection to MonetDB."""
        if not self.connection:
            self.connection = pymonetdb.connect(
                hostname=self.host,
                port=self.port,
                database=self.database,
                username=self.user,
                password=self.password,
                autocommit=False,
            )

    def close(self):
        """Close connection."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None

    def setup_schema(self):
        """Create normalized relational tables for analytical queries."""
        self.connect()
        cursor = self.connection.cursor()

        ddl_statements = [
            """
            CREATE TABLE IF NOT EXISTS movies (
                movie_id INT,
                title VARCHAR(512) NOT NULL,
                release_year SMALLINT,
                PRIMARY KEY (movie_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS genres (
                genre_id INT,
                name VARCHAR(64) NOT NULL UNIQUE,
                PRIMARY KEY (genre_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS movie_genres (
                movie_id INT,
                genre_id INT,
                PRIMARY KEY (movie_id, genre_id),
                FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
                FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS movie_links (
                movie_id INT,
                imdb_id VARCHAR(32),
                tmdb_id VARCHAR(32),
                PRIMARY KEY (movie_id),
                FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS movie_users (
                user_id INT,
                PRIMARY KEY (user_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS ratings (
                user_id INT,
                movie_id INT,
                rating DECIMAL(2,1) NOT NULL,
                rated_at TIMESTAMP,
                PRIMARY KEY (user_id, movie_id),
                FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
                FOREIGN KEY (user_id) REFERENCES movie_users(user_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS tags (
                user_id INT,
                movie_id INT,
                tag VARCHAR(512) NOT NULL,
                tagged_at TIMESTAMP,
                PRIMARY KEY (user_id, movie_id, tag),
                FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
                FOREIGN KEY (user_id) REFERENCES movie_users(user_id)
            );
            """,
        ]

        for stmt in ddl_statements:
            cursor.execute(stmt)
        self.connection.commit()
        cursor.close()
        logger.info("MonetDB schema verified and tables ensured.")

    def load_genres(self, genres: List[str]):
        """Load unique genres, generating sequential deterministic genre_ids."""
        if not genres:
            return
        self.connect()
        cursor = self.connection.cursor()
        
        # Check existing genres
        cursor.execute("SELECT genre_id, name FROM genres")
        existing = {row[1]: row[0] for row in cursor.fetchall()}
        
        next_id = max(existing.values(), default=0) + 1
        new_records = []
        for g in genres:
            if g not in existing:
                new_records.append((next_id, g))
                existing[g] = next_id
                next_id += 1

        if new_records:
            cursor.executemany("INSERT INTO genres (genre_id, name) VALUES (%s, %s)", new_records)
            self.connection.commit()
        cursor.close()

    def get_genre_map(self) -> Dict[str, int]:
        """Fetch mapping of genre name -> genre_id."""
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, genre_id FROM genres")
        genre_map = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        return genre_map

    def load_movies_batch(self, movies_data: List[tuple], movie_genres_data: List[tuple]):
        """
        movies_data: list of (movie_id, title, release_year)
        movie_genres_data: list of (movie_id, genre_id)
        """
        if not movies_data:
            return
        self.connect()
        cursor = self.connection.cursor()
        # Find which movies already exist to ensure idempotency
        movie_ids = [m[0] for m in movies_data]
        format_strings = ",".join(["%s"] * len(movie_ids))
        cursor.execute(f"SELECT movie_id FROM movies WHERE movie_id IN ({format_strings})", movie_ids)
        existing_ids = {row[0] for row in cursor.fetchall()}

        to_insert_movies = [m for m in movies_data if m[0] not in existing_ids]
        if to_insert_movies:
            cursor.executemany(
                "INSERT INTO movies (movie_id, title, release_year) VALUES (%s, %s, %s)",
                to_insert_movies,
            )

        if movie_genres_data:
            # Only insert genre associations for newly added movies
            new_movie_ids = {m[0] for m in to_insert_movies}
            to_insert_genres = [mg for mg in movie_genres_data if mg[0] in new_movie_ids]
            if to_insert_genres:
                cursor.executemany(
                    "INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)",
                    to_insert_genres,
                )

        self.connection.commit()
        cursor.close()

    def load_links_batch(self, links_data: List[tuple]):
        """links_data: list of (movie_id, imdb_id, tmdb_id)"""
        if not links_data:
            return
        self.connect()
        cursor = self.connection.cursor()
        movie_ids = [l[0] for l in links_data]
        format_strings = ",".join(["%s"] * len(movie_ids))
        cursor.execute(f"SELECT movie_id FROM movie_links WHERE movie_id IN ({format_strings})", movie_ids)
        existing_ids = {row[0] for row in cursor.fetchall()}

        to_insert = [l for l in links_data if l[0] not in existing_ids]
        if to_insert:
            cursor.executemany(
                "INSERT INTO movie_links (movie_id, imdb_id, tmdb_id) VALUES (%s, %s, %s)",
                to_insert,
            )
        self.connection.commit()
        cursor.close()

    def load_users_batch(self, user_ids: List[int]):
        """user_ids: list of user_id integers"""
        if not user_ids:
            return
        self.connect()
        cursor = self.connection.cursor()
        format_strings = ",".join(["%s"] * len(user_ids))
        cursor.execute(f"SELECT user_id FROM movie_users WHERE user_id IN ({format_strings})", user_ids)
        existing_ids = {row[0] for row in cursor.fetchall()}

        to_insert = [(uid,) for uid in user_ids if uid not in existing_ids]
        if to_insert:
            cursor.executemany("INSERT INTO movie_users (user_id) VALUES (%s)", to_insert)
        self.connection.commit()
        cursor.close()

    def load_ratings_batch(self, ratings_data: List[tuple]):
        """
        ratings_data: list of (user_id, movie_id, rating, rated_at)
        """
        if not ratings_data:
            return
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.executemany(
                "INSERT INTO ratings (user_id, movie_id, rating, rated_at) VALUES (%s, %s, %s, %s)",
                ratings_data,
            )
            self.connection.commit()
        except pymonetdb.exceptions.IntegrityError:
            self.connection.rollback()
            # Row-by-row fallback or ignore duplicates on rerun
            for r in ratings_data:
                try:
                    cursor.execute(
                        "INSERT INTO ratings (user_id, movie_id, rating, rated_at) VALUES (%s, %s, %s, %s)",
                        r,
                    )
                    self.connection.commit()
                except pymonetdb.exceptions.IntegrityError:
                    self.connection.rollback()
        cursor.close()

    def load_tags_batch(self, tags_data: List[tuple]):
        """
        tags_data: list of (user_id, movie_id, tag, tagged_at)
        """
        if not tags_data:
            return
        self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.executemany(
                "INSERT INTO tags (user_id, movie_id, tag, tagged_at) VALUES (%s, %s, %s, %s)",
                tags_data,
            )
            self.connection.commit()
        except pymonetdb.exceptions.IntegrityError:
            self.connection.rollback()
            for t in tags_data:
                try:
                    cursor.execute(
                        "INSERT INTO tags (user_id, movie_id, tag, tagged_at) VALUES (%s, %s, %s, %s)",
                        t,
                    )
                    self.connection.commit()
                except pymonetdb.exceptions.IntegrityError:
                    self.connection.rollback()
        cursor.close()

    def count_table_rows(self) -> Dict[str, int]:
        """Return row counts for each analytical table."""
        self.connect()
        cursor = self.connection.cursor()
        tables = ["movies", "genres", "movie_genres", "movie_links", "movie_users", "ratings", "tags"]
        counts = {}
        for tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            counts[tbl] = cursor.fetchone()[0]
        cursor.close()
        return counts
