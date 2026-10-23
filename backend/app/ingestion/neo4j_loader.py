import logging
from typing import Dict, List, Optional
from neo4j import GraphDatabase, Driver

logger = logging.getLogger(__name__)


class Neo4jLoader:
    """Manages schema constraints and idempotent batch loading for Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None

    def connect(self):
        """Establish connection to Neo4j."""
        if not self.driver:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()

    def close(self):
        """Close driver connection."""
        if self.driver:
            self.driver.close()
            self.driver = None

    def setup_constraints(self):
        """Create uniqueness constraints and indexes for Movie, Genre, and User nodes."""
        self.connect()
        constraints = [
            "CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.movieId IS UNIQUE",
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE",
            "CREATE CONSTRAINT genre_name_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
            "CREATE INDEX movie_title_idx IF NOT EXISTS FOR (m:Movie) ON (m.title)",
        ]
        with self.driver.session() as session:
            for c in constraints:
                session.run(c)
        logger.info("Neo4j constraints and indexes ensured.")

    def load_genres(self, genres: List[str]):
        """Load unique Genre nodes using UNWIND and MERGE."""
        if not genres:
            return
        self.connect()
        query = """
        UNWIND $batch AS genre_name
        MERGE (g:Genre {name: genre_name})
        """
        with self.driver.session() as session:
            session.run(query, batch=genres)

    def load_movies_batch(self, movies_batch: List[Dict]):
        """
        Batch MERGE movies and link them to their Genre nodes.
        movies_batch item format:
        {
            'movieId': int,
            'title': str,
            'year': int or None,
            'imdbId': str or None,
            'tmdbId': str or None,
            'genres': list of str
        }
        """
        if not movies_batch:
            return
        self.connect()
        query = """
        UNWIND $batch AS item
        MERGE (m:Movie {movieId: item.movieId})
        SET m.title = item.title,
            m.year = item.year,
            m.imdbId = item.imdbId,
            m.tmdbId = item.tmdbId
        WITH m, item.genres AS genres
        UNWIND genres AS genre_name
        MERGE (g:Genre {name: genre_name})
        MERGE (m)-[:IN_GENRE]->(g)
        """
        with self.driver.session() as session:
            session.run(query, batch=movies_batch)

    def load_links_batch(self, links_batch: List[Dict]):
        """
        Update IMDb and TMDb identifiers on existing Movie nodes.
        links_batch item format:
        {'movieId': int, 'imdbId': str or None, 'tmdbId': str or None}
        """
        if not links_batch:
            return
        self.connect()
        query = """
        UNWIND $batch AS item
        MATCH (m:Movie {movieId: item.movieId})
        SET m.imdbId = item.imdbId,
            m.tmdbId = item.tmdbId
        """
        with self.driver.session() as session:
            session.run(query, batch=links_batch)

    def load_users_batch(self, user_ids: List[int]):
        """Create User nodes in batch."""
        if not user_ids:
            return
        self.connect()
        query = """
        UNWIND $batch AS uid
        MERGE (u:User {userId: uid})
        """
        with self.driver.session() as session:
            session.run(query, batch=user_ids)

    def load_ratings_batch(self, ratings_batch: List[Dict]):
        """
        Batch MERGE User nodes, Movie nodes, and (User)-[:RATED]->(Movie) relationships.
        ratings_batch item:
        {'userId': int, 'movieId': int, 'rating': float, 'timestamp': int}
        """
        if not ratings_batch:
            return
        self.connect()
        query = """
        UNWIND $batch AS item
        MERGE (u:User {userId: item.userId})
        MERGE (m:Movie {movieId: item.movieId})
        MERGE (u)-[r:RATED]->(m)
        SET r.rating = item.rating,
            r.timestamp = item.timestamp
        """
        with self.driver.session() as session:
            session.run(query, batch=ratings_batch)

    def load_tags_batch(self, tags_batch: List[Dict]):
        """
        Batch load (User)-[:TAGGED]->(Movie) relationships.
        tags_batch item:
        {'userId': int, 'movieId': int, 'tag': str, 'timestamp': int}
        """
        if not tags_batch:
            return
        self.connect()
        query = """
        UNWIND $batch AS item
        MERGE (u:User {userId: item.userId})
        MERGE (m:Movie {movieId: item.movieId})
        MERGE (u)-[t:TAGGED {tag: item.tag, timestamp: item.timestamp}]->(m)
        """
        with self.driver.session() as session:
            session.run(query, batch=tags_batch)

    def count_entities(self) -> Dict[str, int]:
        """Return counts of nodes and relationships in Neo4j."""
        self.connect()
        counts = {}
        queries = {
            "movies": "MATCH (m:Movie) RETURN count(m) AS cnt",
            "users": "MATCH (u:User) RETURN count(u) AS cnt",
            "genres": "MATCH (g:Genre) RETURN count(g) AS cnt",
            "rated_rels": "MATCH ()-[r:RATED]->() RETURN count(r) AS cnt",
            "tagged_rels": "MATCH ()-[t:TAGGED]->() RETURN count(t) AS cnt",
            "in_genre_rels": "MATCH ()-[g:IN_GENRE]->() RETURN count(g) AS cnt",
        }
        with self.driver.session() as session:
            for key, q in queries.items():
                result = session.run(q).single()
                counts[key] = result["cnt"] if result else 0
        return counts
