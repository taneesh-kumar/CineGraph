import argparse
import json
import logging
import sys
from app.core.config import get_settings
from app.ingestion.dataset_validator import DatasetValidator
from app.ingestion.neo4j_loader import Neo4jLoader
from app.ingestion.monetdb_loader import MonetDBLoader
from app.ingestion.pipeline import IngestionPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("cinegraph-ingestion")


def main():
    parser = argparse.ArgumentParser(description="CineGraph MovieLens Ingestion CLI")
    parser.add_argument(
        "--dataset-dir",
        type=str,
        default=None,
        help="Path to MovieLens CSV directory (default: from .env DATASET_DIR)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size for writing to databases (default: from .env INGESTION_BATCH_SIZE)",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=None,
        help="Limit number of movies loaded for sample mode (0 = full dataset)",
    )
    parser.add_argument(
        "--min-year",
        type=int,
        default=None,
        help="Filter movies to only those released on or after this year (e.g. 2020)",
    )
    parser.add_argument(
        "--max-year",
        type=int,
        default=None,
        help="Filter movies to only those released on or before this year (e.g. 2023)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate dataset files without ingesting into databases",
    )

    args = parser.parse_args()
    settings = get_settings()

    dataset_dir = args.dataset_dir or settings.resolved_dataset_dir
    batch_size = args.batch_size or settings.INGESTION_BATCH_SIZE
    sample_limit = args.sample_limit if args.sample_limit is not None else settings.INGESTION_SAMPLE_LIMIT

    logger.info("=" * 60)
    logger.info("CineGraph MovieLens Ingestion Pipeline")
    logger.info(f"Dataset Directory: {dataset_dir}")
    logger.info(f"Batch Size: {batch_size}")
    logger.info(f"Sample Limit: {'FULL DATASET' if sample_limit == 0 else f'{sample_limit} movies'}")
    if args.min_year or args.max_year:
        logger.info(f"Year Filter: {args.min_year or 'any'} to {args.max_year or 'any'}")
    logger.info("=" * 60)

    validator = DatasetValidator(dataset_dir)
    try:
        validator.validate_files_exist()
        validator.validate_headers()
        stats = validator.get_file_stats()
        logger.info("Dataset files validated successfully:")
        for fname, info in stats.items():
            logger.info(f"  - {fname}: {info['data_rows']:,} rows ({info['size_bytes'] / (1024*1024):.2f} MB)")
    except Exception as e:
        logger.error(f"Dataset validation failed: {e}")
        sys.exit(1)

    if args.validate_only:
        logger.info("Preflight validation complete (--validate-only specified). Exiting.")
        sys.exit(0)

    # Database loaders
    neo4j_loader = Neo4jLoader(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD,
    )
    monetdb_loader = MonetDBLoader(
        host=settings.MONETDB_HOST,
        port=settings.MONETDB_PORT,
        database=settings.MONETDB_DATABASE,
        user=settings.MONETDB_USER,
        password=settings.MONETDB_PASSWORD,
    )

    try:
        pipeline = IngestionPipeline(
            dataset_dir=dataset_dir,
            neo4j_loader=neo4j_loader,
            monetdb_loader=monetdb_loader,
            batch_size=batch_size,
            sample_limit=sample_limit,
            min_year=args.min_year,
            max_year=args.max_year,
        )
        results = pipeline.run()

        logger.info("=" * 60)
        logger.info("INGESTION SUMMARY REPORT")
        logger.info("=" * 60)
        logger.info("Pipeline Metrics:")
        logger.info(json.dumps(results["metrics"], indent=2))
        logger.info("\nNeo4j Entity Counts:")
        logger.info(json.dumps(results["neo4j_counts"], indent=2))
        logger.info("\nMonetDB Table Counts:")
        logger.info(json.dumps(results["monetdb_counts"], indent=2))
        logger.info("=" * 60)

    except Exception as e:
        logger.exception(f"Pipeline encountered a fatal error: {e}")
        sys.exit(1)
    finally:
        neo4j_loader.close()
        monetdb_loader.close()


if __name__ == "__main__":
    main()
