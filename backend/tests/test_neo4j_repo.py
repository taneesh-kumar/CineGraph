import pytest
from unittest.mock import MagicMock
from app.core.exceptions import DatabaseQueryException
from app.repositories.neo4j_repo import Neo4jRepository


@pytest.fixture
def mock_neo4j_session():
    """Mock Neo4j session and driver context manager."""
    session = MagicMock()
    db_manager = MagicMock()
    db_manager.get_neo4j_session.return_value.__enter__.return_value = session
    repo = Neo4jRepository(db_manager=db_manager)
    return repo, session


def test_get_movie_by_id_found(mock_neo4j_session):
    repo, session = mock_neo4j_session
    mock_record = {
        "movie_id": 1,
        "title": "Toy Story (1995)",
        "year": 1995,
        "imdb_id": "0114709",
        "tmdb_id": "862",
        "genres": ["Adventure", "Animation", "Children"],
    }
    result_mock = MagicMock()
    result_mock.single.return_value = mock_record
    session.run.return_value = result_mock

    movie = repo.get_movie_by_id(1)
    assert movie is not None
    assert movie["movie_id"] == 1
    assert movie["title"] == "Toy Story (1995)"
    assert movie["year"] == 1995
    assert movie["imdb_id"] == "0114709"
    assert "Adventure" in movie["genres"]

    # Verify parameterized call
    session.run.assert_called_once()
    args, kwargs = session.run.call_args
    assert kwargs.get("movieId") == 1


def test_get_movie_by_id_not_found(mock_neo4j_session):
    repo, session = mock_neo4j_session
    result_mock = MagicMock()
    result_mock.single.return_value = None
    session.run.return_value = result_mock

    movie = repo.get_movie_by_id(999999)
    assert movie is None


def test_search_movies_by_title(mock_neo4j_session):
    repo, session = mock_neo4j_session
    mock_records = [
        {
            "movie_id": 1,
            "title": "Toy Story (1995)",
            "year": 1995,
            "imdb_id": "0114709",
            "tmdb_id": "862",
            "genres": ["Animation"],
        },
        {
            "movie_id": 3114,
            "title": "Toy Story 2 (1999)",
            "year": 1999,
            "imdb_id": "0120363",
            "tmdb_id": "863",
            "genres": ["Animation"],
        },
    ]
    session.run.return_value = iter(mock_records)

    results = repo.search_movies_by_title("Toy", limit=5)
    assert len(results) == 2
    assert results[0]["title"] == "Toy Story (1995)"

    session.run.assert_called_once()
    args, kwargs = session.run.call_args
    assert kwargs.get("title_query") == "Toy"
    assert kwargs.get("limit") == 5


def test_get_genres_for_movie(mock_neo4j_session):
    repo, session = mock_neo4j_session
    mock_records = [{"genre_name": "Action"}, {"genre_name": "Thriller"}]
    session.run.return_value = iter(mock_records)

    genres = repo.get_genres_for_movie(10)
    assert genres == ["Action", "Thriller"]

    session.run.assert_called_once()
    args, kwargs = session.run.call_args
    assert kwargs.get("movieId") == 10


def test_get_user_ratings(mock_neo4j_session):
    repo, session = mock_neo4j_session
    mock_records = [
        {
            "user_id": 42,
            "movie_id": 1,
            "movie_title": "Toy Story (1995)",
            "rating": 4.5,
            "timestamp": 123456789,
        }
    ]
    session.run.return_value = iter(mock_records)

    ratings = repo.get_user_ratings(42, limit=10)
    assert len(ratings) == 1
    assert ratings[0]["rating"] == 4.5
    assert ratings[0]["user_id"] == 42


def test_get_users_who_rated_movie(mock_neo4j_session):
    repo, session = mock_neo4j_session
    mock_records = [
        {"user_id": 1, "movie_id": 100, "rating": 5.0, "timestamp": 1000},
        {"user_id": 2, "movie_id": 100, "rating": 3.5, "timestamp": 2000},
    ]
    session.run.return_value = iter(mock_records)

    users = repo.get_users_who_rated_movie(100, limit=20)
    assert len(users) == 2
    assert users[0]["user_id"] == 1


def test_get_movies_rated_by_user(mock_neo4j_session):
    repo, session = mock_neo4j_session
    mock_records = [
        {
            "movie_id": 10,
            "title": "GoldenEye (1995)",
            "year": 1995,
            "imdb_id": "0113189",
            "tmdb_id": "710",
            "user_rating": 4.0,
            "rated_timestamp": 99999,
            "genres": ["Action", "Adventure"],
        }
    ]
    session.run.return_value = iter(mock_records)

    movies = repo.get_movies_rated_by_user(5, limit=10)
    assert len(movies) == 1
    assert movies[0]["title"] == "GoldenEye (1995)"
    assert movies[0]["user_rating"] == 4.0


def test_neo4j_query_failure_raises_custom_exception(mock_neo4j_session):
    repo, session = mock_neo4j_session
    session.run.side_effect = Exception("Cypher syntax or connection failure")

    with pytest.raises(DatabaseQueryException) as exc_info:
        repo.get_movie_by_id(1)

    assert "Neo4j" in str(exc_info.value)
