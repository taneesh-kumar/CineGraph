import pytest
from unittest.mock import MagicMock
from app.core.exceptions import EntityNotFoundException
from app.repositories.monetdb_repo import MonetDBRepository
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def mock_monetdb_repo():
    return MagicMock(spec=MonetDBRepository)


@pytest.fixture
def analytics_service(mock_monetdb_repo):
    return AnalyticsService(monetdb_repo=mock_monetdb_repo)


def test_get_top_rated_movies(analytics_service, mock_monetdb_repo):
    mock_monetdb_repo.get_top_rated_movies.return_value = [
        {
            "movie_id": 318,
            "title": "Shawshank Redemption, The (1994)",
            "release_year": 1994,
            "rating_count": 557,
            "avg_rating": 4.41,
        },
        {
            "movie_id": 858,
            "title": "Godfather, The (1972)",
            "release_year": 1972,
            "rating_count": 320,
            "avg_rating": 4.35,
        },
    ]
    mock_monetdb_repo.get_genres_for_movie.side_effect = lambda mid: (
        ["Crime", "Drama"] if mid == 318 else ["Crime", "Drama"]
    )

    results = analytics_service.get_top_rated_movies(min_ratings=50, limit=10)
    assert len(results) == 2
    assert results[0].movie_id == 318
    assert results[0].title == "Shawshank Redemption, The (1994)"
    assert results[0].avg_rating == 4.41
    assert results[0].rating_count == 557
    assert results[0].genres == ["Crime", "Drama"]

    mock_monetdb_repo.get_top_rated_movies.assert_called_once_with(
        min_ratings=50, limit=10
    )


def test_get_genre_popularity(analytics_service, mock_monetdb_repo):
    mock_monetdb_repo.get_genre_popularity.return_value = [
        {
            "genre": "Drama",
            "total_ratings": 21698,
            "distinct_movies": 450,
            "avg_rating": 3.70,
        },
        {
            "genre": "Comedy",
            "total_ratings": 18192,
            "distinct_movies": 380,
            "avg_rating": 3.42,
        },
    ]

    results = analytics_service.get_genre_popularity()
    assert len(results) == 2
    assert results[0].genre == "Drama"
    assert results[0].total_ratings == 21698
    assert results[0].distinct_movies == 450
    assert results[0].avg_rating == 3.70


def test_get_rating_distribution(analytics_service, mock_monetdb_repo):
    mock_monetdb_repo.get_rating_distribution.return_value = [
        {"rating": 3.0, "count": 10000},
        {"rating": 4.0, "count": 15000},
        {"rating": 5.0, "count": 5000},
    ]

    dist = analytics_service.get_rating_distribution()
    assert len(dist) == 3
    # Total count = 30000
    assert dist[0].rating == 3.0
    assert dist[0].count == 10000
    assert dist[0].percentage == 33.33
    assert dist[1].percentage == 50.0
    assert dist[2].percentage == 16.67


def test_get_rating_distribution_empty(analytics_service, mock_monetdb_repo):
    mock_monetdb_repo.get_rating_distribution.return_value = []

    dist = analytics_service.get_rating_distribution()
    assert dist == []


def test_get_movie_stats_found(analytics_service, mock_monetdb_repo):
    mock_monetdb_repo.get_movie_by_id.return_value = {
        "movie_id": 1,
        "title": "Toy Story (1995)",
    }
    mock_monetdb_repo.get_movie_rating_stats.return_value = {
        "movie_id": 1,
        "rating_count": 215,
        "avg_rating": 3.92,
    }

    stats = analytics_service.get_movie_stats(1)
    assert stats.movie_id == 1
    assert stats.rating_count == 215
    assert stats.avg_rating == 3.92


def test_get_movie_stats_not_found(analytics_service, mock_monetdb_repo):
    mock_monetdb_repo.get_movie_by_id.return_value = None

    with pytest.raises(EntityNotFoundException) as exc_info:
        analytics_service.get_movie_stats(999999)

    assert "Movie" in str(exc_info.value)
    assert "999999" in str(exc_info.value)


def test_get_dataset_summary(analytics_service, mock_monetdb_repo):
    mock_monetdb_repo.get_dataset_counts.return_value = {
        "movies": 1000,
        "users": 2364,
        "genres": 19,
        "ratings": 50000,
        "tags": 10000,
    }

    summary = analytics_service.get_dataset_summary()
    assert summary.total_movies == 1000
    assert summary.total_users == 2364
    assert summary.total_genres == 19
    assert summary.total_ratings == 50000
    assert summary.total_tags == 10000
