"""CLI and main entry point for CineGraph Phase 5 Benchmarking & Evaluation."""
import asyncio
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
import click

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.core.database import DatabaseManager
from app.benchmarking.models import BenchmarkConfig, RunManifest
from app.benchmarking.adapters import Neo4jBenchmarkAdapter, MonetDBBenchmarkAdapter
from app.benchmarking.workloads import build_workloads, verify_cross_database_correctness
from app.benchmarking.runner import BenchmarkRunner, run_concurrency_benchmark
from app.benchmarking.storage import BenchmarkStorage
from app.benchmarking.evaluator import evaluate_recommendations_offline
from app.benchmarking.visualizer import BenchmarkVisualizer


@click.group()
def cli():
    """CineGraph Phase 5 Benchmarking, Scalability, and Recommendation Evaluation Suite."""
    pass


@cli.command("run")
@click.option("--warmup", default=3, help="Warm-up iterations to discard from latency metrics.")
@click.option("--repetitions", default=10, help="Measured steady-state iterations per workload.")
@click.option("--output-dir", default="reports/phase-5/results", help="Directory for output artifacts.")
@click.option("--figures-dir", default="reports/phase-5/figures", help="Directory for chart images.")
@click.option("--eval-users", default=30, help="Number of eligible users to evaluate for recommendations.")
def run_all(warmup, repetitions, output_dir, figures_dir, eval_users):
    """Execute complete Phase 5 benchmark suite: database queries, concurrency, and recommendation evaluation."""
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    click.echo(f"============================================================")
    click.echo(f"CINEGRAPH PHASE 5 EXPERIMENTAL BENCHMARK — RUN {run_id}")
    click.echo(f"============================================================")

    config = BenchmarkConfig(
        warmup_iterations=warmup,
        measured_iterations=repetitions,
        output_dir=output_dir,
    )
    storage = BenchmarkStorage(base_output_dir=output_dir)
    visualizer = BenchmarkVisualizer(figures_dir=figures_dir)

    db_manager = DatabaseManager()

    click.echo("\n[1/6] Probing Database Readiness & Metadata...")
    neo4j_ready = db_manager.check_neo4j_health()
    monetdb_ready = db_manager.check_monetdb_health()

    if not (neo4j_ready and monetdb_ready):
        click.echo(f"Error: Databases unavailable. Neo4j: {neo4j_ready}, MonetDB: {monetdb_ready}", err=True)
        sys.exit(1)

    # Collect dataset metadata
    with db_manager.get_monetdb_cursor() as cur:
        cur.execute("SELECT count(*) FROM movies")
        movie_cnt = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM ratings")
        rating_cnt = cur.fetchone()[0]
        cur.execute("SELECT count(DISTINCT user_id) FROM movie_users")
        user_cnt = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM genres")
        genre_cnt = cur.fetchone()[0]

    dataset_metadata = {
        "movies": movie_cnt,
        "ratings": rating_cnt,
        "users": user_cnt,
        "genres": genre_cnt,
        "release_window": "2020-2023",
    }
    click.echo(f"Dataset Verified: {movie_cnt} movies, {rating_cnt} ratings, {user_cnt} users, {genre_cnt} genres.")

    # --------------------------------------------------------------------------
    # 2. Database Workloads Execution
    # --------------------------------------------------------------------------
    click.echo("\n[2/6] Executing Workloads A through E (Neo4j & MonetDB)...")
    neo4j_adapter = Neo4jBenchmarkAdapter(db_manager)
    monetdb_adapter = MonetDBBenchmarkAdapter(db_manager)

    sample_movie_ids = [217465, 225173, 210861]  # Tenet, Soul, The Gentlemen
    sample_user_ids = [57304, 139018, 8901]

    workloads = build_workloads(neo4j_adapter, monetdb_adapter, sample_movie_ids, sample_user_ids)
    runner = BenchmarkRunner(config, run_id)

    all_raw_measurements = []
    summary_metrics = []

    for w in workloads:
        click.echo(f"  -> Running {w.workload_id} ({w.target_engine.value})...", nl=False)
        raws, metrics = runner.run_workload(w)
        all_raw_measurements.extend(raws)
        summary_metrics.append(metrics)
        click.echo(f" done. Median: {metrics.median_ms:.2f} ms | Mean: {metrics.mean_ms:.2f} ms | p95: {metrics.p95_ms:.2f} ms")

    # --------------------------------------------------------------------------
    # 3. Cross-Database Correctness Verification
    # --------------------------------------------------------------------------
    click.echo("\n[3/6] Verifying Cross-Database Logical Correctness...")
    correctness_results = verify_cross_database_correctness(neo4j_adapter, monetdb_adapter, movie_id=217465)
    for c in correctness_results:
        status_str = "MATCH" if (c.counts_match and c.data_matches) else "MISMATCH"
        click.echo(f"  [{status_str}] {c.workload_id}: Neo4j count={c.neo4j_count}, MonetDB count={c.monetdb_count}")

    # --------------------------------------------------------------------------
    # 4. Concurrency Scalability Benchmark
    # --------------------------------------------------------------------------
    click.echo("\n[4/6] Executing Concurrency & Throughput Harness (1, 2, 5, 10 clients)...")
    try:
        concurrency_results = asyncio.run(run_concurrency_benchmark(
            base_url="http://127.0.0.1:8000",
            concurrency_levels=[1, 2, 5, 10],
            requests_per_level=20,
        ))
        for cr in concurrency_results:
            click.echo(f"  Concurrency {cr['concurrency']}: {cr['throughput_req_per_sec']} req/s | Median: {cr['median_latency_ms']} ms | p95: {cr['p95_latency_ms']} ms")
    except Exception as e:
        click.echo(f"  Warning: Live server concurrency run skipped ({e}). Ensure FastAPI is running on port 8000.")
        concurrency_results = []

    # --------------------------------------------------------------------------
    # 5. Offline Recommendation Evaluation
    # --------------------------------------------------------------------------
    click.echo("\n[5/6] Running Offline Recommendation Evaluation (Temporal Split without Leakage)...")
    eval_metrics = evaluate_recommendations_offline(
        db_manager,
        k_values=[5, 10],
        relevance_threshold=4.0,
        max_users_to_evaluate=eval_users,
    )
    for em in eval_metrics:
        click.echo(
            f"  {em.model_name} @ K={em.k}: Precision={em.precision:.4f} | Recall={em.recall:.4f} | "
            f"NDCG={em.ndcg:.4f} | HitRate={em.hit_rate:.4f} | Coverage={em.catalog_coverage:.1f}%"
        )

    # --------------------------------------------------------------------------
    # 6. Artifact Persistence & Visualizations
    # --------------------------------------------------------------------------
    click.echo("\n[6/6] Persisting Artifacts & Generating 2D Charts...")
    raw_path = storage.save_raw_measurements(run_id, all_raw_measurements)
    sum_path = storage.save_summary_metrics(run_id, summary_metrics)
    cor_path = storage.save_correctness_results(run_id, correctness_results)
    ev_path = storage.save_recommendation_evaluation(run_id, eval_metrics)

    manifest = RunManifest(
        run_id=run_id,
        timestamp=datetime.utcnow(),
        python_version=platform.python_version(),
        dataset_metadata=dataset_metadata,
        config=config,
        summary_metrics_file=str(sum_path),
        raw_measurements_file=str(raw_path),
    )
    man_path = storage.save_manifest(manifest)

    # Render Visualizations
    fig1 = visualizer.plot_query_latency(summary_metrics)
    fig2 = visualizer.plot_latency_percentiles(summary_metrics)
    fig3 = visualizer.plot_concurrency_throughput(concurrency_results)
    fig4 = visualizer.plot_recommendation_metrics(eval_metrics)

    click.echo(f"Saved Raw Measurements: {raw_path}")
    click.echo(f"Saved Summary Metrics: {sum_path}")
    click.echo(f"Saved Manifest: {man_path}")
    click.echo(f"Rendered Figures in: {figures_dir}")
    click.echo("Benchmark execution completed successfully.")

    db_manager.close_neo4j_driver()


if __name__ == "__main__":
    cli()
