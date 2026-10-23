import logging
from typing import List, Optional
from app.repositories.neo4j_repo import Neo4jRepository
from app.core.exceptions import EntityNotFoundException
from app.schemas.services import RecommendationItem, RecommendationResult

logger = logging.getLogger("cinegraph-recommendation-service")


class RecommendationService:
    """
    Recommendation service providing graph-based recommendations using Neo4j.
    Supports:
    1. Content/genre similarity with rating evidence.
    2. Collaborative user-personalized recommendations based on peer rating patterns.
    """

    def __init__(self, neo4j_repo: Neo4jRepository):
        self.neo4j_repo = neo4j_repo

    def get_similar_movies(
        self,
        movie_id: int,
        limit: int = 10,
    ) -> RecommendationResult:
        """
        Recommend movies sharing genres with source movie.
        Excludes the source movie itself.
        Ranks candidates by:
          score = shared_genre_count * 2.0 + (avg_rating * 0.5)
        """
        source_movie = self.neo4j_repo.get_movie_by_id(movie_id)
        if not source_movie:
            raise EntityNotFoundException("Movie", movie_id)

        candidates = self.neo4j_repo.get_similar_movies_by_genres(movie_id, limit=limit)
        items: List[RecommendationItem] = []

        for c in candidates:
            if c["movie_id"] == movie_id:
                continue
            shared_genres = c.get("shared_genres", [])
            shared_count = c.get("shared_genre_count", len(shared_genres))
            avg_rating = c.get("avg_rating", 0.0)
            score = round((shared_count * 2.0) + (avg_rating * 0.5), 2)

            genre_str = ", ".join(shared_genres) if shared_genres else "themes"
            explanation = (
                f"Shares {shared_count} genre(s) ({genre_str}) with '{source_movie['title']}'"
            )
            if avg_rating > 0.0:
                explanation += f" with an average rating of {avg_rating}/5.0"

            items.append(
                RecommendationItem(
                    movie_id=c["movie_id"],
                    title=c["title"],
                    year=c.get("year"),
                    genres=c.get("genres", []),
                    score=score,
                    explanation=explanation,
                    imdb_id=c.get("imdb_id"),
                    tmdb_id=c.get("tmdb_id"),
                )
            )

        # Deterministic ranking: score descending, then title ascending
        items.sort(key=lambda x: (-x.score, x.title))

        return RecommendationResult(
            source_type="movie",
            source_id=movie_id,
            source_title=source_movie["title"],
            recommendations=items[:limit],
            total_found=len(items),
        )

    def get_user_recommendations(
        self,
        user_id: int,
        limit: int = 10,
    ) -> RecommendationResult:
        """
        Provide personalized recommendations for a user.
        Uses collaborative signals: peers who also rated movies liked by this user (>= 3.5).
        Falls back to favorite genre expansion if collaborative peer signals are insufficient.
        Excludes any movie the user has already rated.
        """
        user_ratings = self.neo4j_repo.get_user_ratings(user_id, limit=200)
        rated_movie_ids = {r["movie_id"] for r in user_ratings}

        # 1. Attempt collaborative filtering traversal
        collab_candidates = self.neo4j_repo.get_collaborative_candidates(
            user_id=user_id,
            min_user_rating=3.5,
            limit=limit * 2,
        )

        items: List[RecommendationItem] = []

        for c in collab_candidates:
            if c["movie_id"] in rated_movie_ids:
                continue

            peer_count = c.get("peer_count", 1)
            peer_avg = c.get("peer_avg_rating", 3.5)
            # Score formula based on peer support and average peer rating
            score = round((peer_count * 1.5) + (peer_avg * 1.0), 2)
            explanation = (
                f"Recommended based on {peer_count} user(s) with similar rating taste "
                f"who rated this movie an average of {peer_avg}/5.0"
            )

            items.append(
                RecommendationItem(
                    movie_id=c["movie_id"],
                    title=c["title"],
                    year=c.get("year"),
                    genres=c.get("genres", []),
                    score=score,
                    explanation=explanation,
                    imdb_id=c.get("imdb_id"),
                    tmdb_id=c.get("tmdb_id"),
                )
            )

        # 2. Fallback if collaborative signals are sparse (e.g. cold/sparse user)
        if len(items) < limit and user_ratings:
            # Pick user's highest-rated movie as seed for genre similarity
            best_rating = max(user_ratings, key=lambda r: r["rating"])
            seed_movie_id = best_rating["movie_id"]
            seed_title = best_rating.get("movie_title", f"Movie #{seed_movie_id}")

            genre_sims = self.neo4j_repo.get_similar_movies_by_genres(
                seed_movie_id, limit=limit * 2
            )
            existing_ids = {item.movie_id for item in items} | rated_movie_ids

            for gs in genre_sims:
                if gs["movie_id"] in existing_ids:
                    continue
                shared_genres = gs.get("shared_genres", [])
                score = round((len(shared_genres) * 1.0) + (gs.get("avg_rating", 0.0) * 0.4), 2)
                genre_str = ", ".join(shared_genres) if shared_genres else "genres"
                explanation = (
                    f"Recommended based on your rating for '{seed_title}' (shares {genre_str})"
                )

                items.append(
                    RecommendationItem(
                        movie_id=gs["movie_id"],
                        title=gs["title"],
                        year=gs.get("year"),
                        genres=gs.get("genres", []),
                        score=score,
                        explanation=explanation,
                        imdb_id=gs.get("imdb_id"),
                        tmdb_id=gs.get("tmdb_id"),
                    )
                )
                existing_ids.add(gs["movie_id"])
                if len(items) >= limit:
                    break

        items.sort(key=lambda x: (-x.score, x.title))

        return RecommendationResult(
            source_type="user",
            source_id=user_id,
            source_title=f"User #{user_id}",
            recommendations=items[:limit],
            total_found=len(items[:limit]),
        )
