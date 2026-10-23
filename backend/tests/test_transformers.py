import pytest
from datetime import datetime
from app.ingestion.transformers import Transformers


def test_extract_year_and_title():
    # Regular title with 4-digit year
    title, year = Transformers.extract_year_and_title("Toy Story (1995)")
    assert title == "Toy Story"
    assert year == 1995

    # Title with nested parentheses
    title2, year2 = Transformers.extract_year_and_title("Babylon 5: The Gathering (1993)")
    assert title2 == "Babylon 5: The Gathering"
    assert year2 == 1993

    # Title without year
    title3, year3 = Transformers.extract_year_and_title("Cosmos")
    assert title3 == "Cosmos"
    assert year3 is None


def test_parse_genres():
    # Multi-genre pipe-separated
    genres = Transformers.parse_genres("Adventure|Animation|Children|Comedy|Fantasy")
    assert genres == ["Adventure", "Animation", "Children", "Comedy", "Fantasy"]

    # Special handling for (no genres listed)
    assert Transformers.parse_genres("(no genres listed)") == []
    assert Transformers.parse_genres("") == []
    assert Transformers.parse_genres(None) == []


def test_parse_timestamp():
    dt = Transformers.parse_timestamp("964982703")
    assert isinstance(dt, datetime)
    assert dt.year == 2000
    assert Transformers.parse_timestamp("invalid") is None


def test_sanitizers():
    assert Transformers.sanitize_id(" 12345 ") == 12345
    assert Transformers.sanitize_id("invalid") is None
    assert Transformers.sanitize_float(" 4.5 ") == 4.5
    assert Transformers.sanitize_float("invalid") is None
    assert Transformers.sanitize_str("  hello  ") == "hello"
    assert Transformers.sanitize_str("   ") is None
    assert Transformers.sanitize_str(None) is None
