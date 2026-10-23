"""
Benchmark script to measure response latencies across CineGraph REST endpoints.
Records cold-start vs. warm query latencies and statistics across repetitions.
"""

import asyncio
import json
import statistics
import time
from typing import Dict, List, Tuple
from httpx import ASGITransport, AsyncClient
from app.main import app

ENDPOINTS: List[Tuple[str, str, Dict[str, any]]] = [
    (
        "Liveness Probe",
        "/api/v1/health",
        {},
    ),
    (
        "Readiness Probe",
        "/api/v1/ready",
        {},
    ),
    (
        "Similar-Movie Recommendations",
        "/api/v1/recommendations/movie/1?limit=10",
        {"target": "Toy Story (1)"},
    ),
    (
        "Personalized Recommendations",
        "/api/v1/recommendations/user/1?limit=10",
        {"target": "User 1"},
    ),
    (
        "Top-Rated Movies",
        "/api/v1/analytics/top-rated?min_ratings=20&limit=20",
        {"filter": "min_ratings=20"},
    ),
    (
        "Genre Popularity",
        "/api/v1/analytics/genres",
        {},
    ),
    (
        "Rating Distribution",
        "/api/v1/analytics/ratings/distribution",
        {},
    ),
    (
        "Movie Rating Statistics",
        "/api/v1/analytics/movies/1/ratings",
        {"target": "Movie 1"},
    ),
    (
        "Dataset Summary",
        "/api/v1/analytics/summary",
        {},
    ),
]


async def run_benchmark(repetitions: int = 10):
    transport = ASGITransport(app=app)
    results = []

    async with AsyncClient(transport=transport, base_url="http://benchmark") as client:
        # Pre-flight check
        ready_res = await client.get("/api/v1/ready")
        if ready_res.status_code != 200:
            print("Databases not ready for benchmarking:", ready_res.text)
            return

        print("=" * 80)
        print(f"CineGraph Phase 3.4 API Latency Benchmark ({repetitions} runs per endpoint)")
        print("Dataset: 1,000 movies, 2,364 users, 50,000 ratings, 10,000 tags")
        print("=" * 80)

        for name, path, meta in ENDPOINTS:
            latencies = []
            cold_latency = None

            for i in range(repetitions):
                start = time.perf_counter()
                res = await client.get(path)
                elapsed_ms = (time.perf_counter() - start) * 1000.0

                if res.status_code != 200:
                    print(f"ERROR on {path}: {res.status_code} - {res.text}")
                    break

                if i == 0:
                    cold_latency = elapsed_ms
                latencies.append(elapsed_ms)

            warm_latencies = latencies[1:] if len(latencies) > 1 else latencies
            mean_warm = statistics.mean(warm_latencies)
            median_warm = statistics.median(warm_latencies)
            min_lat = min(latencies)
            max_lat = max(latencies)

            res_entry = {
                "endpoint_name": name,
                "path": path,
                "repetitions": len(latencies),
                "cold_ms": round(cold_latency, 2) if cold_latency else 0.0,
                "mean_warm_ms": round(mean_warm, 2),
                "median_warm_ms": round(median_warm, 2),
                "min_ms": round(min_lat, 2),
                "max_ms": round(max_lat, 2),
            }
            results.append(res_entry)
            print(
                f"{name:<35} | Cold: {res_entry['cold_ms']:>6.2f} ms | "
                f"Warm Mean: {res_entry['mean_warm_ms']:>6.2f} ms | "
                f"Min: {res_entry['min_ms']:>6.2f} ms | Max: {res_entry['max_ms']:>6.2f} ms"
            )

        print("=" * 80)
        with open("benchmark_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print("Benchmark results saved to backend/benchmark_results.json")


if __name__ == "__main__":
    asyncio.run(run_benchmark(repetitions=10))
