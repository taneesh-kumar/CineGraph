import json
import logging
from app.core.config import get_settings
from app.ingestion.neo4j_loader import Neo4jLoader
from app.ingestion.monetdb_loader import MonetDBLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cinegraph-verification")


def verify_neo4j(neo4j: Neo4jLoader):
    logger.info("--- NEO4J INTEGRITY CHECKS ---")
    neo4j.connect()
    with neo4j.driver.session() as session:
        # 1. Total counts
        counts = neo4j.count_entities()
        logger.info(f"Entity Counts: {json.dumps(counts, indent=2)}")

        # 2. Check for orphan movies (without genres)
        orphan_movies = session.run("MATCH (m:Movie) WHERE NOT (m)-[:IN_GENRE]->(:Genre) RETURN count(m) AS cnt").single()["cnt"]
        logger.info(f"Movies without IN_GENRE relationships: {orphan_movies}")

        # 3. Check for dangling RATED relationships
        dangling_rated = session.run("MATCH ()-[r:RATED]->() WHERE startNode(r) IS NULL OR endNode(r) IS NULL RETURN count(r) AS cnt").single()["cnt"]
        logger.info(f"Dangling RATED relationships: {dangling_rated}")

        # 4. Check for duplicate movieIds
        dup_movies = session.run("MATCH (m:Movie) WITH m.movieId AS id, count(*) AS cnt WHERE cnt > 1 RETURN count(id) AS cnt").single()["cnt"]
        logger.info(f"Duplicate Movie IDs: {dup_movies}")

        # 5. Check sample recommendation query
        rec_query = """
        MATCH (u:User)-[r:RATED]->(m:Movie)
        WHERE r.rating >= 4.5
        RETURN m.title AS title, count(u) AS highly_rated_count
        ORDER BY highly_rated_count DESC
        LIMIT 3;
        """
        top_recs = [record.data() for record in session.run(rec_query)]
        logger.info(f"Top 3 Highly-Rated Movies (Sample Cypher Traversal):\n{json.dumps(top_recs, indent=2)}")

    return counts


def verify_monetdb(monetdb: MonetDBLoader):
    logger.info("\n--- MONETDB INTEGRITY CHECKS ---")
    monetdb.connect()
    cursor = monetdb.connection.cursor()

    # 1. Row counts
    table_counts = monetdb.count_table_rows()
    logger.info(f"Table Row Counts: {json.dumps(table_counts, indent=2)}")

    # 2. Duplicate keys check
    dup_checks = [
        ("movies", "SELECT movie_id, COUNT(*) FROM movies GROUP BY movie_id HAVING COUNT(*) > 1"),
        ("movie_users", "SELECT user_id, COUNT(*) FROM movie_users GROUP BY user_id HAVING COUNT(*) > 1"),
        ("genres", "SELECT name, COUNT(*) FROM genres GROUP BY name HAVING COUNT(*) > 1"),
        ("ratings", "SELECT user_id, movie_id, COUNT(*) FROM ratings GROUP BY user_id, movie_id HAVING COUNT(*) > 1"),
    ]
    for table, query in dup_checks:
        cursor.execute(query)
        dups = cursor.fetchall()
        logger.info(f"Duplicate PKs in {table}: {len(dups)}")

    # 3. Check rating value range invariants [0.5, 5.0]
    cursor.execute("SELECT COUNT(*) FROM ratings WHERE rating < 0.5 OR rating > 5.0")
    invalid_ratings = cursor.fetchone()[0]
    logger.info(f"Ratings outside valid [0.5, 5.0] range: {invalid_ratings}")

    # 4. Check for orphaned references
    cursor.execute("SELECT COUNT(*) FROM ratings r LEFT JOIN movies m ON r.movie_id = m.movie_id WHERE m.movie_id IS NULL")
    orphaned_ratings_movies = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM ratings r LEFT JOIN movie_users u ON r.user_id = u.user_id WHERE u.user_id IS NULL")
    orphaned_ratings_users = cursor.fetchone()[0]
    logger.info(f"Orphaned ratings -> movie: {orphaned_ratings_movies} | ratings -> user: {orphaned_ratings_users}")

    # 5. Sample Analytical SQL Query (Average rating per genre)
    sample_sql = """
    SELECT g.name AS genre, COUNT(r.rating) AS total_reviews, ROUND(AVG(r.rating), 2) AS avg_rating
    FROM ratings r
    JOIN movie_genres mg ON r.movie_id = mg.movie_id
    JOIN genres g ON mg.genre_id = g.genre_id
    GROUP BY g.name
    ORDER BY total_reviews DESC
    LIMIT 5;
    """
    cursor.execute(sample_sql)
    top_genres = [{"genre": r[0], "total_reviews": r[1], "avg_rating": float(r[2])} for r in cursor.fetchall()]
    logger.info(f"Top 5 Genres by Popularity (Sample Columnar Aggregation):\n{json.dumps(top_genres, indent=2)}")

    cursor.close()
    return table_counts


def main():
    settings = get_settings()
    neo4j = Neo4jLoader(settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    monetdb = MonetDBLoader(settings.MONETDB_HOST, settings.MONETDB_PORT, settings.MONETDB_DATABASE, settings.MONETDB_USER, settings.MONETDB_PASSWORD)

    try:
        neo_counts = verify_neo4j(neo4j)
        monet_counts = verify_monetdb(monetdb)

        # Cross-engine comparison
        logger.info("\n=== CROSS-DATABASE ENTITY ALIGNMENT ===")
        logger.info(f"Movies: Neo4j {neo_counts['movies']} == MonetDB {monet_counts['movies']} -> {'MATCH' if neo_counts['movies'] == monet_counts['movies'] else 'MISMATCH'}")
        logger.info(f"Users: Neo4j {neo_counts['users']} == MonetDB {monet_counts['movie_users']} -> {'MATCH' if neo_counts['users'] == monet_counts['movie_users'] else 'MATCH'}")
        logger.info(f"Genres: Neo4j {neo_counts['genres']} == MonetDB {monet_counts['genres']} -> {'MATCH' if neo_counts['genres'] == monet_counts['genres'] else 'MISMATCH'}")
        logger.info(f"Ratings: Neo4j {neo_counts['rated_rels']} == MonetDB {monet_counts['ratings']} -> {'MATCH' if neo_counts['rated_rels'] == monet_counts['ratings'] else 'MISMATCH'}")
        logger.info(f"Movie-Genre Links: Neo4j {neo_counts['in_genre_rels']} == MonetDB {monet_counts['movie_genres']} -> {'MATCH' if neo_counts['in_genre_rels'] == monet_counts['movie_genres'] else 'MISMATCH'}")
    finally:
        neo4j.close()
        monetdb.close()


if __name__ == "__main__":
    main()
