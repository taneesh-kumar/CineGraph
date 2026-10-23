import datetime
import pytest
from unittest.mock import MagicMock
from app.core.exceptions import DatabaseQueryException
from app.repositories.monetdb_repo import MonetDBRepository


@pytest.fixture
def mock_monetdb_cursor():
    """Mock MonetDB cursor and database manager context manager."""
    cursor = MagicMock()
    db_manager = MagicMock()
    db_manager.get_monetdb_cursor.return_value.__enter__.return_value = cursor
    repo = MonetDBRepository(db_manager=db_manager)
    return repo, cursor


def test_get_movie_by_id_found(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    # row format: (movie_id, title, release_year, imdb_id, tmdb_id)
    cursor.fetchone.return_value = (1, "Toy Story (1995)", 1995, "0114709", "862")
    cursor.fetchall.return_value = [("Adventure",), ("Animation",), ("Children",)]

    movie = repo.get_movie_by_id(1)
    assert movie is not None
    assert movie["movie_id"] == 1
    assert movie["title"] == "Toy Story (1995)"
    assert movie["year"] == 1995
    assert movie["imdb_id"] == "0114709"
    assert movie["genres"] == ["Adventure", "Animation", "Children"]

    assert cursor.execute.call_count == 2
    args1, _ = cursor.execute.call_args_list[0]
    assert args1[1] == (1,)


def test_get_movie_by_id_not_found(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    cursor.fetchone.return_value = None

    movie = repo.get_movie_by_id(999999)
    assert movie is None


def test_search_movies_by_title(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    cursor.fetchall.return_value = [
        (1, "Toy Story (1995)", 1995, "0114709", "862"),
        (3114, "Toy Story 2 (1999)", 1999, "0120363", "863"),
    ]

    movies = repo.search_movies_by_title("Toy", limit=10)
    assert len(movies) == 2
    assert movies[0]["title"] == "Toy Story (1995)"
    assert movies[1]["year"] == 1999

    cursor.execute.assert_called_once()
    sql, params = cursor.execute.call_args[0]
    assert params == ("%Toy%", 10)


def test_get_genres_for_movie(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    cursor.fetchall.return_value = [("Comedy",), ("Drama",)]

    genres = repo.get_genres_for_movie(5)
    assert genres == ["Comedy", "Drama"]

    cursor.execute.assert_called_once()
    _, params = cursor.execute.call_args[0]
    assert params == (5,)


def test_get_ratings_for_movie(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    dt = datetime.datetime(2023, 1, 1, 12, 0, 0)
    cursor.fetchall.return_value = [
        (101, 1, 4.5, dt),
        (102, 1, 3.0, dt),
    ]

    ratings = repo.get_ratings_for_movie(1, limit=5)
    assert len(ratings) == 2
    assert ratings[0]["user_id"] == 101
    assert ratings[0]["rating"] == 4.5
    assert ratings[0]["rated_at"] == dt.isoformat()

    cursor.execute.assert_called_once()
    _, params = cursor.execute.call_args[0]
    assert params == (1, 5)


def test_get_ratings_by_user(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    dt = datetime.datetime(2023, 5, 10, 8, 30, 0)
    cursor.fetchall.return_value = [
        (42, 1, "Toy Story (1995)", 5.0, dt),
    ]

    ratings = repo.get_ratings_by_user(42, limit=20)
    assert len(ratings) == 1
    assert ratings[0]["user_id"] == 42
    assert ratings[0]["movie_title"] == "Toy Story (1995)"
    assert ratings[0]["rating"] == 5.0

    cursor.execute.assert_called_once()
    _, params = cursor.execute.call_args[0]
    assert params == (42, 20)


def test_get_movie_rating_stats(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    cursor.fetchone.return_value = (150, 4.1234)

    stats = repo.get_movie_rating_stats(1)
    assert stats is not None
    assert stats["movie_id"] == 1
    assert stats["rating_count"] == 150
    assert stats["avg_rating"] == 4.12


def test_get_movie_rating_stats_no_ratings(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    cursor.fetchone.return_value = (0, None)

    stats = repo.get_movie_rating_stats(999)
    assert stats["movie_id"] == 999
    assert stats["rating_count"] == 0
    assert stats["avg_rating"] == 0.0


def test_monetdb_query_failure_raises_custom_exception(mock_monetdb_cursor):
    repo, cursor = mock_monetdb_cursor
    cursor.execute.side_effect = Exception("Column does not exist or database timeout")

    with pytest.raises(DatabaseQueryException) as exc_info:
        repo.get_movie_by_id(1)

    assert "MonetDB" in str(exc_info.value)
