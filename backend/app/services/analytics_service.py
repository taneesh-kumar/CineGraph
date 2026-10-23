import logging
from typing import Dict, List, Optional
from app.repositories.monetdb_repo import MonetDBRepository
from app.core.exceptions import EntityNotFoundException
from app.schemas.services import (
    TopRatedMovie,
    GenrePopularity,
    RatingDistributionItem,
    DatasetSummary,
)
from app.schemas.common import MovieRatingStats

logger = logging.getLogger("cinegraph-analytics-service")


class AnalyticsService:
    """
    Analytics service providing SQL-powered columnar aggregations using MonetDB.
    All aggregations run inside the database engine.
    """

    def __init__(self, monetdb_repo: MonetDBRepository):
        self.monetdb_repo = monetdb_repo

    def get_top_rated_movies(
        self,
        min_ratings: int = 10,
        limit: int = 20,
    ) -> List[TopRatedMovie]:
        """
        Fetch top rated movies filtered by minimum rating threshold.
        Enriches each movie with its genres.
        """
        raw_movies = self.monetdb_repo.get_top_rated_movies(
            min_ratings=min_ratings,
            limit=limit,
        )

        results: List[TopRatedMovie] = []
        for rm in raw_movies:
            genres = self.monetdb_repo.get_genres_for_movie(rm["movie_id"])
            results.append(
                TopRatedMovie(
                    movie_id=rm["movie_id"],
                    title=rm["title"],
                    release_year=rm["release_year"],
                    avg_rating=rm["avg_rating"],
                    rating_count=rm["rating_count"],
                    genres=genres,
                )
            )
        return results

    def get_genre_popularity(self) -> List[GenrePopularity]:
        """
        Return popularity metrics across all genres:
        Total ratings recorded, count of distinct movies rated, and average rating.
        """
        raw_genres = self.monetdb_repo.get_genre_popularity()
        return [
            GenrePopularity(
                genre=g["genre"],
                total_ratings=g["total_ratings"],
                distinct_movies=g["distinct_movies"],
                avg_rating=g["avg_rating"],
            )
            for g in raw_genres
        ]

    def get_rating_distribution(self) -> List[RatingDistributionItem]:
        """
        Return frequency distribution across discrete MovieLens ratings (0.5 to 5.0).
        Calculates percentage share of each rating value.
        """
        raw_dist = self.monetdb_repo.get_rating_distribution()
        total_count = sum(item["count"] for item in raw_dist)

        results: List[RatingDistributionItem] = []
        for item in raw_dist:
            count = item["count"]
            percentage = round((count / total_count * 100.0), 2) if total_count > 0 else 0.0
            results.append(
                RatingDistributionItem(
                    rating=item["rating"],
                    count=count,
                    percentage=percentage,
                )
            )
        return results

    def get_movie_stats(self, movie_id: int) -> MovieRatingStats:
        """
        Return rating statistics for a single movie.
        Raises EntityNotFoundException if movie does not exist.
        """
        movie = self.monetdb_repo.get_movie_by_id(movie_id)
        if not movie:
            raise EntityNotFoundException("Movie", movie_id)

        stats = self.monetdb_repo.get_movie_rating_stats(movie_id)
        return MovieRatingStats(
            movie_id=movie_id,
            rating_count=stats["rating_count"] if stats else 0,
            avg_rating=stats["avg_rating"] if stats else 0.0,
        )

    def get_dataset_summary(self) -> DatasetSummary:
        """
        Return global database summary counts across movies, users, genres, ratings, and tags.
        """
        counts = self.monetdb_repo.get_dataset_counts()
        return DatasetSummary(
            total_movies=counts["movies"],
            total_users=counts["users"],
            total_genres=counts["genres"],
            total_ratings=counts["ratings"],
            total_tags=counts["tags"],
        )
