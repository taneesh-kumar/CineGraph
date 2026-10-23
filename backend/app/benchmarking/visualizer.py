"""Visualizer generating matplotlib charts and figures for Phase 5 reporting."""
from pathlib import Path
from typing import Any, Dict, List
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from app.benchmarking.models import WorkloadMetrics, RecommendationEvalMetrics


class BenchmarkVisualizer:
    """Generates clean, publishable 2D figures from benchmark and evaluation outputs."""

    def __init__(self, figures_dir: str = "reports/phase-5/figures"):
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def plot_query_latency(self, metrics: List[WorkloadMetrics]) -> Path:
        """Bar plot comparing median latency across key database workloads."""
        out_path = self.figures_dir / "query-latency.png"
        
        # Select representative workloads
        selected = [m for m in metrics if "nomatch" not in m.workload_id][:10]
        if not selected:
            return out_path

        labels = [m.operation.replace("_", " ").title()[:20] for m in selected]
        medians = [m.median_ms for m in selected]
        colors = ["#4f46e5" if m.target_engine.value == "neo4j" else "#10b981" for m in selected]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.barh(labels, medians, color=colors, edgecolor="#1f2937", height=0.6)
        ax.set_xlabel("Median Latency (ms)", fontsize=11, fontweight="bold")
        ax.set_title("Database Query Execution Latency (Neo4j vs MonetDB)", fontsize=13, fontweight="bold", pad=12)
        ax.grid(axis="x", linestyle="--", alpha=0.4)

        # Annotate bar values
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height() / 2, f"{width:.2f} ms",
                    va="center", ha="left", fontsize=9, color="#111827")

        plt.tight_layout()
        plt.savefig(out_path, dpi=200)
        plt.close()
        return out_path

    def plot_latency_percentiles(self, metrics: List[WorkloadMetrics]) -> Path:
        """Chart showing min, median, p90, and p95 percentiles for workloads."""
        out_path = self.figures_dir / "latency-percentiles.png"
        selected = [m for m in metrics if "nomatch" not in m.workload_id][:8]
        if not selected:
            return out_path

        ops = [m.operation.replace("_", " ").title()[:18] for m in selected]
        p50 = [m.median_ms for m in selected]
        p90 = [m.p90_ms for m in selected]
        p95 = [m.p95_ms for m in selected]

        import numpy as np
        x = np.arange(len(ops))
        width = 0.25

        fig, ax = plt.subplots(figsize=(11, 5.5))
        ax.bar(x - width, p50, width, label="p50 (Median)", color="#6366f1")
        ax.bar(x, p90, width, label="p90", color="#f59e0b")
        ax.bar(x + width, p95, width, label="p95", color="#ef4444")

        ax.set_ylabel("Latency (ms)", fontsize=11, fontweight="bold")
        ax.set_title("Latency Distribution Percentiles by Workload", fontsize=13, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(ops, rotation=25, ha="right", fontsize=9)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()
        plt.savefig(out_path, dpi=200)
        plt.close()
        return out_path

    def plot_concurrency_throughput(self, concurrency_results: List[Dict[str, Any]]) -> Path:
        """Line chart showing concurrency vs throughput (req/sec)."""
        out_path = self.figures_dir / "concurrency-throughput.png"
        if not concurrency_results:
            return out_path

        c_levels = [r["concurrency"] for r in concurrency_results]
        throughput = [r["throughput_req_per_sec"] for r in concurrency_results]
        latencies = [r["median_latency_ms"] for r in concurrency_results]

        fig, ax1 = plt.subplots(figsize=(8, 4.5))

        color = "#4f46e5"
        ax1.set_xlabel("Concurrency Level (Concurrent Clients)", fontsize=11, fontweight="bold")
        ax1.set_ylabel("Throughput (req/sec)", color=color, fontsize=11, fontweight="bold")
        ax1.plot(c_levels, throughput, marker="o", color=color, linewidth=2, label="Throughput")
        ax1.tick_params(axis="y", labelcolor=color)
        ax1.grid(True, linestyle="--", alpha=0.4)

        ax2 = ax1.twinx()
        color = "#e11d48"
        ax2.set_ylabel("Median Latency (ms)", color=color, fontsize=11, fontweight="bold")
        ax2.plot(c_levels, latencies, marker="s", color=color, linewidth=2, linestyle="--", label="Latency")
        ax2.tick_params(axis="y", labelcolor=color)

        plt.title("API Throughput & Latency Scaling vs Concurrency", fontsize=12, fontweight="bold", pad=12)
        plt.tight_layout()
        plt.savefig(out_path, dpi=200)
        plt.close()
        return out_path

    def plot_recommendation_metrics(self, eval_results: List[RecommendationEvalMetrics]) -> Path:
        """Bar plot comparing recommendation models across Precision, Recall, and NDCG."""
        out_path = self.figures_dir / "recommendation-metrics.png"
        if not eval_results:
            return out_path

        import numpy as np
        # Group by K=10
        k10_results = [r for r in eval_results if r.k == 10]
        if not k10_results:
            k10_results = eval_results[:2]

        models = [r.model_name.replace(" Baseline", "").replace(" Model", "") for r in k10_results]
        precision = [r.precision for r in k10_results]
        recall = [r.recall for r in k10_results]
        ndcg = [r.ndcg for r in k10_results]

        x = np.arange(len(models))
        width = 0.25

        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar(x - width, precision, width, label="Precision@10", color="#3b82f6")
        ax.bar(x, recall, width, label="Recall@10", color="#10b981")
        ax.bar(x + width, ndcg, width, label="NDCG@10", color="#8b5cf6")

        ax.set_ylabel("Score", fontsize=11, fontweight="bold")
        ax.set_title("Offline Recommendation Ranking Quality (K=10)", fontsize=12, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(models, fontsize=10)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()
        plt.savefig(out_path, dpi=200)
        plt.close()
        return out_path
