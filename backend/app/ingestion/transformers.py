import re
from datetime import datetime
from typing import List, Optional, Tuple


YEAR_PATTERN = re.compile(r"\((\d{4})\)\s*$")


class Transformers:
    """Utility transformations for MovieLens data records."""

    @staticmethod
    def extract_year_and_title(raw_title: str) -> Tuple[str, Optional[int]]:
        """
        Extract clean title and 4-digit release year from a title like 'Toy Story (1995)'.
        If no year is present, returns (raw_title, None).
        """
        clean_title = raw_title.strip()
        match = YEAR_PATTERN.search(clean_title)
        if match:
            year = int(match.group(1))
            title = clean_title[:match.start()].strip()
            return title, year
        return clean_title, None

    @staticmethod
    def parse_genres(raw_genres: str) -> List[str]:
        """
        Split pipe-separated genre string, filtering out '(no genres listed)'.
        """
        if not raw_genres:
            return []
        items = [g.strip() for g in raw_genres.split("|") if g.strip()]
        # Filter out placeholder indicating missing genres
        return [g for g in items if g.lower() != "(no genres listed)"]

    @staticmethod
    def parse_timestamp(raw_timestamp: str) -> Optional[datetime]:
        """Convert Unix epoch seconds into datetime."""
        try:
            return datetime.utcfromtimestamp(int(raw_timestamp))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def sanitize_id(raw_id: str) -> Optional[int]:
        """Parse integer ID or return None."""
        try:
            val = int(raw_id.strip())
            return val
        except (ValueError, TypeError, AttributeError):
            return None

    @staticmethod
    def sanitize_float(raw_val: str) -> Optional[float]:
        """Parse float value or return None."""
        try:
            return float(raw_val.strip())
        except (ValueError, TypeError, AttributeError):
            return None

    @staticmethod
    def sanitize_str(raw_val: Optional[str]) -> Optional[str]:
        """Clean string or return None if empty."""
        if raw_val is None:
            return None
        s = raw_val.strip()
        return s if s else None
