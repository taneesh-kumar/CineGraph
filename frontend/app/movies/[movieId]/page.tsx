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
import { EngineBadge } from "@/components/ui/EngineBadge";
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
      <div className="rounded-2xl border border-neutral-800/80 bg-gradient-to-br from-neutral-900/90 via-neutral-900/50 to-neutral-950 p-6 sm:p-8 space-y-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="font-mono text-neutral-400 bg-neutral-800/80 px-2 py-0.5 rounded border border-neutral-700">
                MovieLens ID: {movie.movie_id}
              </span>
              <EngineBadge engine="neo4j" size="sm" />
              {(movie.year || movie.release_year) && (
                <span className="flex items-center gap-1 text-neutral-400 font-medium">
                  <Calendar className="h-3 w-3" />
                  {movie.year || movie.release_year}
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              {movie.title}
            </h1>

            {/* Genres */}
            <div className="flex flex-wrap gap-2 pt-1">
              {movie.genres && movie.genres.length > 0 ? (
                movie.genres.map((g) => (
                  <span
                    key={g}
                    className="inline-flex items-center rounded-lg bg-neutral-800/90 px-3 py-1 text-xs font-semibold text-neutral-200 border border-neutral-700/60"
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
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-500 transition-colors"
            >
              <Sparkles className="h-4 w-4" />
              <span>Explore Graph Traversal</span>
            </Link>
          </div>
        </div>

        {/* Rating Metrics Bar (Powered by MonetDB) */}
        <div className="pt-6 border-t border-neutral-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="rounded-xl bg-neutral-900/80 border border-neutral-800 p-4">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-1">
              <span>Average Rating</span>
              <EngineBadge engine="monetdb" size="sm" showIcon={false} />
            </div>
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 text-amber-400 fill-amber-400" />
              <span className="text-2xl font-bold text-white">
                {(ratingAnalytics?.avg_rating ?? ratingAnalytics?.average_rating) !== null &&
                (ratingAnalytics?.avg_rating ?? ratingAnalytics?.average_rating) !== undefined
                  ? (ratingAnalytics?.avg_rating ?? ratingAnalytics?.average_rating)!.toFixed(2)
                  : "N/A"}
              </span>
              <span className="text-xs text-neutral-500">/ 5.0</span>
            </div>
          </div>

          <div className="rounded-xl bg-neutral-900/80 border border-neutral-800 p-4">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-1">
              <span>Rating Count</span>
              <EngineBadge engine="monetdb" size="sm" showIcon={false} />
            </div>
            <div className="text-2xl font-bold text-white font-mono">
              {ratingAnalytics?.rating_count ? ratingAnalytics.rating_count.toLocaleString() : "0"}
            </div>
            <div className="text-[11px] text-neutral-500">ratings in sample</div>
          </div>

          <div className="rounded-xl bg-neutral-900/80 border border-neutral-800 p-4">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-1">
              <span>Min Rating</span>
              <EngineBadge engine="monetdb" size="sm" showIcon={false} />
            </div>
            <div className="text-2xl font-bold text-neutral-200 font-mono">
              {ratingAnalytics?.min_rating !== null && ratingAnalytics?.min_rating !== undefined
                ? ratingAnalytics.min_rating.toFixed(1)
                : "—"}
            </div>
            <div className="text-[11px] text-neutral-500">lowest awarded</div>
          </div>

          <div className="rounded-xl bg-neutral-900/80 border border-neutral-800 p-4">
            <div className="flex items-center justify-between text-xs text-neutral-400 mb-1">
              <span>Max Rating</span>
              <EngineBadge engine="monetdb" size="sm" showIcon={false} />
            </div>
            <div className="text-2xl font-bold text-neutral-200 font-mono">
              {ratingAnalytics?.max_rating !== null && ratingAnalytics?.max_rating !== undefined
                ? ratingAnalytics.max_rating.toFixed(1)
                : "—"}
            </div>
            <div className="text-[11px] text-neutral-500">highest awarded</div>
          </div>
        </div>
      </div>

      {/* Similar Movies Section (Powered by Neo4j Graph Walk) */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-400" />
              Similar Movies via Neo4j Graph Traversal
            </h2>
            <p className="text-xs text-neutral-400">
              Computed via Jaccard similarity across shared genre paths and co-rating community nodes
            </p>
          </div>
          <EngineBadge engine="neo4j" />
        </div>

        {recommendations?.recommendations && recommendations.recommendations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.recommendations.map((rec) => (
              <div
                key={rec.movie_id}
                className="flex flex-col justify-between rounded-xl border border-neutral-800 bg-neutral-900/60 p-5 hover:border-neutral-700 hover:bg-neutral-900 transition-colors"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs text-neutral-400">
                    <span className="font-mono text-neutral-400">ID #{rec.movie_id}</span>
                    <span className="rounded bg-indigo-500/10 px-2 py-0.5 font-mono font-bold text-indigo-400 border border-indigo-500/20">
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
            description="The graph topology for this movie did not return neighbors with sufficient similarity in the 1,000-movie development sample."
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
