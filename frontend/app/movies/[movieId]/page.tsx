"use client";

import { useEffect, useState, use, Suspense } from "react";
import Link from "next/link";
import {
  Star,
  Sparkles,
  ArrowLeft,
  Calendar,
  ExternalLink,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";
import {
  MovieSummary,
  MovieRatingAnalytics,
  RecommendationResult,
} from "@/lib/types";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";

interface PageProps {
  params: Promise<{ movieId: string }>;
}

function MovieDetailsContent({ params }: PageProps) {
  const resolvedParams = use(params);
  const movieIdStr = resolvedParams.movieId;
  const movieId = parseInt(movieIdStr, 10);

  const [movie, setMovie] = useState<MovieSummary | null>(null);
  const [ratingAnalytics, setRatingAnalytics] = useState<MovieRatingAnalytics | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isNaN(movieId) || movieId <= 0) {
      setError(`Invalid Movie ID: "${movieIdStr}". Movie ID must be a positive integer.`);
      setIsLoading(false);
      return;
    }

    const loadMovieDetails = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Fetch movie metadata, MonetDB rating analytics, and Neo4j recommendations in parallel
        const [movieRes, ratingsRes, recsRes] = await Promise.allSettled([
          apiClient.getMovieById(movieId),
          apiClient.getMovieRatingAnalytics(movieId),
          apiClient.getMovieRecommendations(movieId, 6),
        ]);

        if (movieRes.status === "fulfilled") {
          setMovie(movieRes.value);
        } else {
          throw new Error(`Movie with ID ${movieId} was not found in the dataset sample.`);
        }

        if (ratingsRes.status === "fulfilled") {
          setRatingAnalytics(ratingsRes.value);
        }

        if (recsRes.status === "fulfilled") {
          setRecommendations(recsRes.value);
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to load movie details";
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    };

    loadMovieDetails();
  }, [movieId, movieIdStr]);

  if (isLoading) {
    return (
      <div className="py-16">
        <LoadingState message={`Fetching details for Movie ID #${movieIdStr} across Neo4j and MonetDB...`} />
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="py-8 space-y-4">
        <Link
          href="/movies"
          className="inline-flex items-center gap-2 text-sm text-neutral-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Movie Explorer</span>
        </Link>
        <ErrorState
          title="Movie Not Found"
          message={error || `Movie #${movieIdStr} does not exist in the ingested development sample.`}
        />
      </div>
    );
  }

  return (
    <div className="space-y-10">
      {/* Back button */}
      <div>
        <Link
          href="/movies"
          className="inline-flex items-center gap-2 text-sm text-neutral-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Movie Explorer</span>
        </Link>
      </div>

      {/* Main Movie Hero Banner */}
      <div className="relative rounded-3xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/90 via-neutral-900/60 to-neutral-950/95 p-6 sm:p-10 space-y-8 backdrop-blur-md shadow-2xl shadow-black/50 overflow-hidden">
        {/* Decorative ambient top glow */}
        <div className="absolute top-0 left-1/4 right-1/4 h-[1px] bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />

        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="space-y-4 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2.5 text-xs">
              <span className="font-mono text-neutral-300 bg-neutral-800/80 px-2.5 py-1 rounded-full border border-neutral-700/60">
                Movie ID: {movie.movie_id}
              </span>
              {(movie.year || movie.release_year) && (
                <span className="flex items-center gap-1.5 text-neutral-300 bg-neutral-800/60 px-2.5 py-1 rounded-full border border-neutral-700/50 font-medium">
                  <Calendar className="h-3.5 w-3.5 text-indigo-400" />
                  {movie.year || movie.release_year}
                </span>
              )}
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
              {movie.title}
            </h1>

            {/* Genres */}
            <div className="flex flex-wrap gap-2 pt-1">
              {movie.genres && movie.genres.length > 0 ? (
                movie.genres.map((g) => (
                  <span
                    key={g}
                    className="inline-flex items-center rounded-full bg-neutral-800/80 px-3.5 py-1 text-xs font-semibold text-neutral-200 border border-neutral-700/70 shadow-sm"
                  >
                    {g}
                  </span>
                ))
              ) : (
                <span className="text-xs text-neutral-500 italic">No genres registered</span>
              )}
            </div>
          </div>

          {/* Quick Action Button to Recommendations */}
          <div className="flex flex-col gap-2 shrink-0">
            <Link
              href={`/recommendations?movie_id=${movie.movie_id}`}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 hover:bg-indigo-500 hover:shadow-indigo-600/50 transition-all cursor-pointer"
            >
              <Sparkles className="h-4 w-4" />
              <span>View Recommendations</span>
            </Link>
          </div>
        </div>

        {/* Rating Metrics Bar */}
        <div className="pt-8 border-t border-neutral-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="rounded-2xl bg-neutral-950/80 border border-neutral-800/90 p-5 shadow-md">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-2 font-medium">
              <span>Average Rating</span>
            </div>
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 text-amber-400 fill-amber-400" />
              <span className="text-3xl font-bold text-white font-mono">
                {(ratingAnalytics?.avg_rating ?? ratingAnalytics?.average_rating) !== null &&
                (ratingAnalytics?.avg_rating ?? ratingAnalytics?.average_rating) !== undefined
                  ? (ratingAnalytics?.avg_rating ?? ratingAnalytics?.average_rating)!.toFixed(2)
                  : "N/A"}
              </span>
              <span className="text-xs text-neutral-500 font-mono">/ 5.0</span>
            </div>
          </div>

          <div className="rounded-2xl bg-neutral-950/80 border border-neutral-800/90 p-5 shadow-md">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-2 font-medium">
              <span>Rating Count</span>
            </div>
            <div className="text-3xl font-bold text-white font-mono">
              {ratingAnalytics?.rating_count ? ratingAnalytics.rating_count.toLocaleString() : "0"}
            </div>
            <div className="text-[11px] text-neutral-500 mt-0.5">total ratings</div>
          </div>

          <div className="rounded-2xl bg-neutral-950/80 border border-neutral-800/90 p-5 shadow-md">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-2 font-medium">
              <span>Min Rating</span>
            </div>
            <div className="text-3xl font-bold text-neutral-200 font-mono">
              {ratingAnalytics?.min_rating !== null && ratingAnalytics?.min_rating !== undefined
                ? ratingAnalytics.min_rating.toFixed(1)
                : "—"}
            </div>
            <div className="text-[11px] text-neutral-500 mt-0.5">lowest awarded</div>
          </div>

          <div className="rounded-2xl bg-neutral-950/80 border border-neutral-800/90 p-5 shadow-md">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-2 font-medium">
              <span>Max Rating</span>
            </div>
            <div className="text-3xl font-bold text-neutral-200 font-mono">
              {ratingAnalytics?.max_rating !== null && ratingAnalytics?.max_rating !== undefined
                ? ratingAnalytics.max_rating.toFixed(1)
                : "—"}
            </div>
            <div className="text-[11px] text-neutral-500 mt-0.5">highest awarded</div>
          </div>
        </div>
      </div>

      {/* Similar Movies Section */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-400" />
              Similar Movies
            </h2>
            <p className="text-xs text-neutral-400">
              Recommended titles based on genre similarity and user ratings
            </p>
          </div>
        </div>

        {recommendations?.recommendations && recommendations.recommendations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {recommendations.recommendations.map((rec) => (
              <div
                key={rec.movie_id}
                className="group relative flex flex-col justify-between rounded-2xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/90 via-neutral-900/60 to-neutral-950/90 p-5 shadow-lg backdrop-blur-md hover:border-neutral-700 hover:-translate-y-1 transition-all duration-200 overflow-hidden"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-neutral-400">
                    <span className="font-mono text-neutral-400">ID #{rec.movie_id}</span>
                    <span className="rounded-full bg-indigo-500/15 px-2.5 py-0.5 font-mono font-bold text-indigo-300 border border-indigo-500/30">
                      Score: {rec.score.toFixed(3)}
                    </span>
                  </div>

                  <Link
                    href={`/movies/${rec.movie_id}`}
                    className="font-bold text-white text-base hover:text-indigo-300 transition-colors line-clamp-1 block"
                  >
                    {rec.title}
                  </Link>

                  {/* Shared Genres & Explanation */}
                  <div className="flex flex-wrap gap-1 pt-1">
                    {rec.genres.map((g) => (
                      <span
                        key={g}
                        className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                          movie.genres.includes(g)
                            ? "bg-indigo-950/80 text-indigo-300 border border-indigo-800/60"
                            : "bg-neutral-800 text-neutral-400"
                        }`}
                      >
                        {g}
                      </span>
                    ))}
                  </div>

                  {rec.explanation && (
                    <p className="text-xs text-neutral-400 bg-neutral-950/60 p-2.5 rounded-lg border border-neutral-850 italic">
                      &ldquo;{rec.explanation}&rdquo;
                    </p>
                  )}
                </div>

                <div className="pt-3 mt-3 border-t border-neutral-800 flex items-center justify-between text-xs">
                  <span className="text-[11px] text-neutral-500">Algorithm: {recommendations.algorithm}</span>
                  <Link
                    href={`/movies/${rec.movie_id}`}
                    className="text-indigo-400 hover:text-indigo-300 font-medium inline-flex items-center gap-1"
                  >
                    <span>View Movie</span>
                    <ExternalLink className="h-3 w-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No Similar Movies Found"
            description="The graph topology for this movie did not return neighbors with sufficient similarity in the active 2,500-movie dataset sample."
          />
        )}
      </section>
    </div>
  );
}

export default function MovieDetailsPage({ params }: PageProps) {
  return (
    <Suspense fallback={<LoadingState message="Loading movie details..." />}>
      <MovieDetailsContent params={params} />
    </Suspense>
  );
}
