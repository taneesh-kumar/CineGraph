import pytest
from unittest.mock import MagicMock
from app.core.exceptions import EntityNotFoundException
from app.repositories.neo4j_repo import Neo4jRepository
from app.services.recommendation_service import RecommendationService


@pytest.fixture
def mock_neo4j_repo():
    return MagicMock(spec=Neo4jRepository)


@pytest.fixture
def rec_service(mock_neo4j_repo):
    return RecommendationService(neo4j_repo=mock_neo4j_repo)


def test_get_similar_movies_success(rec_service, mock_neo4j_repo):
    # Mock source movie
    mock_neo4j_repo.get_movie_by_id.return_value = {
        "movie_id": 1,
        "title": "Toy Story (1995)",
        "genres": ["Adventure", "Animation", "Children"],
    }
    # Mock similar candidates
    mock_neo4j_repo.get_similar_movies_by_genres.return_value = [
        {
            "movie_id": 3114,
            "title": "Toy Story 2 (1999)",
            "year": 1999,
            "shared_genre_count": 3,
            "shared_genres": ["Adventure", "Animation", "Children"],
            "genres": ["Adventure", "Animation", "Children", "Comedy"],
            "rating_count": 250,
            "avg_rating": 4.1,
            "imdb_id": "0120363",
            "tmdb_id": "863",
        },
        {
            "movie_id": 2355,
            "title": "Bug's Life, A (1998)",
            "year": 1998,
            "shared_genre_count": 2,
            "shared_genres": ["Animation", "Children"],
            "genres": ["Animation", "Children", "Comedy"],
            "rating_count": 180,
            "avg_rating": 3.8,
            "imdb_id": "0120623",
            "tmdb_id": "9487",
        },
    ]

    res = rec_service.get_similar_movies(movie_id=1, limit=5)
    assert res.source_id == 1
    assert res.source_title == "Toy Story (1995)"
    assert len(res.recommendations) == 2

    top = res.recommendations[0]
    assert top.movie_id == 3114
    assert top.score > res.recommendations[1].score
    assert "Shares 3 genre(s)" in top.explanation
    assert "Adventure, Animation, Children" in top.explanation
    assert "4.1/5.0" in top.explanation


def test_get_similar_movies_excludes_source_movie(rec_service, mock_neo4j_repo):
    mock_neo4j_repo.get_movie_by_id.return_value = {
        "movie_id": 10,
        "title": "GoldenEye (1995)",
        "genres": ["Action", "Adventure", "Thriller"],
    }
    mock_neo4j_repo.get_similar_movies_by_genres.return_value = [
        {
            "movie_id": 10,  # simulate if graph returned self
            "title": "GoldenEye (1995)",
            "shared_genre_count": 3,
            "shared_genres": ["Action", "Adventure", "Thriller"],
            "avg_rating": 3.5,
        },
        {
            "movie_id": 20,
            "title": "Money Train (1995)",
            "shared_genre_count": 2,
            "shared_genres": ["Action", "Thriller"],
            "avg_rating": 3.0,
        },
    ]

    res = rec_service.get_similar_movies(movie_id=10, limit=5)
    rec_ids = [r.movie_id for r in res.recommendations]
    assert 10 not in rec_ids
    assert 20 in rec_ids


def test_get_similar_movies_missing_movie_raises(rec_service, mock_neo4j_repo):
    mock_neo4j_repo.get_movie_by_id.return_value = None

    with pytest.raises(EntityNotFoundException) as exc_info:
        rec_service.get_similar_movies(movie_id=999999)

    assert "Movie" in str(exc_info.value)
    assert "999999" in str(exc_info.value)


def test_get_user_recommendations_collaborative(rec_service, mock_neo4j_repo):
    mock_neo4j_repo.get_user_ratings.return_value = [
        {"movie_id": 1, "rating": 5.0, "movie_title": "Toy Story (1995)"},
        {"movie_id": 2, "rating": 4.0, "movie_title": "Jumanji (1995)"},
    ]
    mock_neo4j_repo.get_collaborative_candidates.return_value = [
        {
            "movie_id": 3114,
            "title": "Toy Story 2 (1999)",
            "year": 1999,
            "peer_count": 15,
            "peer_avg_rating": 4.3,
            "genres": ["Animation", "Children"],
            "imdb_id": "0120363",
            "tmdb_id": "863",
        },
        {
            "movie_id": 1,  # Already rated by user -> must be excluded!
            "title": "Toy Story (1995)",
            "year": 1995,
            "peer_count": 50,
            "peer_avg_rating": 4.5,
            "genres": ["Animation"],
        },
    ]

    res = rec_service.get_user_recommendations(user_id=42, limit=5)
    assert res.source_type == "user"
    assert res.source_id == 42
    # Already-rated movie 1 must be excluded
    rec_ids = [r.movie_id for r in res.recommendations]
    assert 1 not in rec_ids
    assert 3114 in rec_ids
    assert "15 user(s) with similar rating taste" in res.recommendations[0].explanation


def test_get_user_recommendations_empty_history(rec_service, mock_neo4j_repo):
    mock_neo4j_repo.get_user_ratings.return_value = []
    mock_neo4j_repo.get_collaborative_candidates.return_value = []

    res = rec_service.get_user_recommendations(user_id=99999, limit=5)
    assert res.source_id == 99999
    assert res.recommendations == []
    assert res.total_found == 0


def test_get_user_recommendations_fallback_genre_expansion(rec_service, mock_neo4j_repo):
    # Collaborative candidates are empty, but user has rated a movie
    mock_neo4j_repo.get_user_ratings.return_value = [
        {"movie_id": 1, "rating": 5.0, "movie_title": "Toy Story (1995)"}
    ]
    mock_neo4j_repo.get_collaborative_candidates.return_value = []
    mock_neo4j_repo.get_similar_movies_by_genres.return_value = [
        {
            "movie_id": 3114,
            "title": "Toy Story 2 (1999)",
            "year": 1999,
            "shared_genres": ["Animation", "Children"],
            "genres": ["Animation", "Children"],
            "avg_rating": 4.2,
        }
    ]

    res = rec_service.get_user_recommendations(user_id=10, limit=5)
    assert len(res.recommendations) == 1
    assert res.recommendations[0].movie_id == 3114
    assert "Recommended based on your rating for 'Toy Story (1995)'" in res.recommendations[0].explanation
