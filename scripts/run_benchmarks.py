"""Root script for running Phase 5 benchmarks."""
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.benchmarking.cli import cli

if __name__ == "__main__":
    cli()
