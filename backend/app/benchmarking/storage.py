"""Storage management for raw benchmark measurements and manifests."""
import csv
import json
import os
from pathlib import Path
from typing import List
from app.benchmarking.models import (
    RawMeasurement,
    WorkloadMetrics,
    RunManifest,
    CorrectnessComparison,
    RecommendationEvalMetrics,
)


class BenchmarkStorage:
    """Handles serialization and persistence of benchmark measurements and summaries."""

    def __init__(self, base_output_dir: str = "reports/phase-5/results"):
        self.base_output_dir = Path(base_output_dir)

    def create_run_directory(self, run_id: str) -> Path:
        run_dir = self.base_output_dir / f"run-{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def save_raw_measurements(self, run_id: str, measurements: List[RawMeasurement]) -> Path:
        run_dir = self.create_run_directory(run_id)
        file_path = run_dir / "raw-benchmarks.csv"

        if not measurements:
            return file_path

        fieldnames = [
            "timestamp",
            "run_id",
            "workload_id",
            "operation",
            "target_engine",
            "execution_mode",
            "repetition_index",
            "is_warmup",
            "duration_ms",
            "success",
            "result_count",
            "error_message",
            "parameters",
        ]

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for m in measurements:
                row = m.model_dump()
                row["timestamp"] = m.timestamp.isoformat()
                row["target_engine"] = m.target_engine.value
                row["execution_mode"] = m.execution_mode.value
                row["parameters"] = json.dumps(m.parameters)
                writer.writerow(row)

        return file_path

    def save_summary_metrics(self, run_id: str, metrics: List[WorkloadMetrics]) -> Path:
        run_dir = self.create_run_directory(run_id)
        file_path = run_dir / "benchmark-summary.json"
        data = [m.model_dump() for m in metrics]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return file_path

    def save_correctness_results(self, run_id: str, results: List[CorrectnessComparison]) -> Path:
        run_dir = self.create_run_directory(run_id)
        file_path = run_dir / "correctness-results.json"
        data = [r.model_dump() for r in results]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return file_path

    def save_recommendation_evaluation(
        self, run_id: str, results: List[RecommendationEvalMetrics]
    ) -> Path:
        run_dir = self.create_run_directory(run_id)
        file_path = run_dir / "recommendation-evaluation.json"
        data = [r.model_dump() for r in results]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return file_path

    def save_manifest(self, manifest: RunManifest) -> Path:
        run_dir = self.create_run_directory(manifest.run_id)
        file_path = run_dir / "manifest.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(mode="json"), f, indent=2)
        return file_path

    def list_runs(self) -> List[str]:
        if not self.base_output_dir.exists():
            return []
        runs = []
        for p in self.base_output_dir.iterdir():
            if p.is_dir() and p.name.startswith("run-"):
                runs.append(p.name.replace("run-", ""))
        return sorted(runs)
