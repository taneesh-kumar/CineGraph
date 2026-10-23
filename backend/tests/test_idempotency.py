import pytest
from app.ingestion.transformers import Transformers


def test_idempotent_transformations():
    """Verify that multiple passes of transformations yield deterministic identical outputs."""
    raw_title = "Heat (1995)"
    title1, year1 = Transformers.extract_year_and_title(raw_title)
    title2, year2 = Transformers.extract_year_and_title(raw_title)
    assert title1 == title2 == "Heat"
    assert year1 == year2 == 1995

    raw_genres = "Action|Crime|Thriller"
    genres1 = Transformers.parse_genres(raw_genres)
    genres2 = Transformers.parse_genres(raw_genres)
    assert genres1 == genres2 == ["Action", "Crime", "Thriller"]


def test_duplicate_handling_logic():
    """Verify that list-to-set conversion and deduplication patterns prevent duplicates."""
    sample_users = [101, 102, 103, 101, 102, 104]
    deduped = list(dict.fromkeys(sample_users))
    assert deduped == [101, 102, 103, 104]
