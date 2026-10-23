import csv
import os
from typing import Dict, List, Tuple


REQUIRED_FILES = {
    "movies.csv": ["movieId", "title", "genres"],
    "ratings.csv": ["userId", "movieId", "rating", "timestamp"],
    "tags.csv": ["userId", "movieId", "tag", "timestamp"],
    "links.csv": ["movieId", "imdbId", "tmdbId"],
}


class DatasetValidationError(Exception):
    """Exception raised when dataset files fail integrity checks."""
    pass


class DatasetValidator:
    """Validates the MovieLens 32M raw dataset directory and schema integrity."""

    def __init__(self, dataset_dir: str):
        self.dataset_dir = dataset_dir

    def validate_files_exist(self) -> List[str]:
        """Check that all required files exist in the dataset directory."""
        missing = []
        for filename in REQUIRED_FILES.keys():
            full_path = os.path.join(self.dataset_dir, filename)
            if not os.path.isfile(full_path):
                missing.append(filename)
        if missing:
            raise DatasetValidationError(
                f"Missing required dataset files in '{self.dataset_dir}': {missing}"
            )
        return list(REQUIRED_FILES.keys())

    def validate_headers(self) -> Dict[str, List[str]]:
        """Validate that CSV headers match expected column definitions."""
        detected_headers = {}
        for filename, expected_cols in REQUIRED_FILES.items():
            full_path = os.path.join(self.dataset_dir, filename)
            with open(full_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    raise DatasetValidationError(f"File {filename} is empty or unparseable.")
                # Strip potential BOM or whitespace
                cleaned_header = [col.strip().lstrip("\ufeff") for col in header]
                if cleaned_header != expected_cols:
                    raise DatasetValidationError(
                        f"Schema mismatch in {filename}: expected {expected_cols}, got {cleaned_header}"
                    )
                detected_headers[filename] = cleaned_header
        return detected_headers

    def get_file_stats(self) -> Dict[str, Dict[str, any]]:
        """Compute row counts and file sizes without loading all data into memory."""
        stats = {}
        for filename in REQUIRED_FILES.keys():
            full_path = os.path.join(self.dataset_dir, filename)
            size_bytes = os.path.getsize(full_path)
            row_count = 0
            with open(full_path, mode="r", encoding="utf-8") as f:
                # Fast line counter
                for _ in f:
                    row_count += 1
            # Subtract 1 for the header line
            data_rows = max(0, row_count - 1)
            stats[filename] = {
                "size_bytes": size_bytes,
                "data_rows": data_rows,
                "path": full_path,
            }
        return stats
