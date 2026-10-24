"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import {
  BarChart3,
  Star,
  Film,
  Users,
  Tags,
  Search,
  ArrowRight,
  TrendingUp,
  Table as TableIcon,
  BarChart2,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";
import {
  DatasetSummary,
  TopRatedMovie,
  GenrePopularity,
  RatingDistributionItem,
  MovieRatingAnalytics,
  MovieSummary,
} from "@/lib/types";
import { StatCard } from "@/components/ui/StatCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { MovieAutocomplete } from "@/components/movies/MovieAutocomplete";

export default function AnalyticsDashboard() {
  // Global analytics state
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [topMovies, setTopMovies] = useState<TopRatedMovie[]>([]);
  const [genres, setGenres] = useState<GenrePopularity[]>([]);
  const [distribution, setDistribution] = useState<RatingDistributionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Top-rated filter controls
  const [minRatings, setMinRatings] = useState(10);
  const [topRatedLimit, setTopRatedLimit] = useState(10);
  const [isTopRatedLoading, setIsTopRatedLoading] = useState(false);

  // View toggle for genres: Chart vs Table
  const [genreView, setGenreView] = useState<"chart" | "table">("chart");

  // Movie deep-dive lookup
  const [lookupMovie, setLookupMovie] = useState<MovieSummary | null>({
    movie_id: 217465,
    title: "Tenet",
    year: 2020,
    genres: ["Action", "Sci-Fi"],
  });
  const [movieAnalytics, setMovieAnalytics] = useState<MovieRatingAnalytics | null>(null);
  const [isLookupLoading, setIsLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);
  // Initial load
  useEffect(() => {
    const fetchAllAnalytics = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [sumRes, topRes, genRes, distRes] = await Promise.all([
          apiClient.getDatasetSummary(),
          apiClient.getTopRatedMovies(minRatings, topRatedLimit),
          apiClient.getGenrePopularity(15),
          apiClient.getRatingDistribution(),
        ]);
        setSummary(sumRes);
        setTopMovies(topRes);
        setGenres(genRes);
        setDistribution(distRes);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Failed to load analytics data";
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllAnalytics();
  }, []);

  // Filter change for Top-Rated
  const handleFilterTopRated = async (minR: number, lim: number) => {
    setMinRatings(minR);
    setTopRatedLimit(lim);
    setIsTopRatedLoading(true);
    try {
      const updated = await apiClient.getTopRatedMovies(minR, lim);
      setTopMovies(updated);
    } catch (err) {
      console.error("Failed to update top rated movies:", err);
    } finally {
      setIsTopRatedLoading(false);
    }
  };

  const fetchMovieAnalytics = async (movie: MovieSummary) => {
    setIsLookupLoading(true);
    setLookupError(null);
    try {
      const data = await apiClient.getMovieRatingAnalytics(movie.movie_id);
      setMovieAnalytics(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Movie rating analytics not found";
      setLookupError(msg);
      setMovieAnalytics(null);
    } finally {
      setIsLookupLoading(false);
    }
  };

  // Run initial movie lookup on mount
  useEffect(() => {
    fetchMovieAnalytics({
      movie_id: 217465,
      title: "Tenet",
      year: 2020,
      genres: ["Action", "Sci-Fi"],
    });
  }, []);

  // Compute total ratings in distribution for percentage calculations
  const totalDistributionRatings = useMemo(() => {
    return distribution.reduce((sum, item) => sum + item.count, 0);
  }, [distribution]);

  const maxDistributionCount = useMemo(() => {
    return Math.max(...distribution.map((d) => d.count), 1);
  }, [distribution]);

  const maxGenreCount = useMemo(() => {
    return Math.max(...genres.map((g) => g.total_ratings ?? g.rating_count ?? 0), 1);
  }, [genres]);

  return (
    <div className="space-y-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-emerald-400" />
            Analytics Dashboard
          </h1>
          <p className="text-sm text-neutral-400 mt-1">
            Aggregations, rating distributions, and trend insights across movies.
          </p>
        </div>
      </div>

      {isLoading ? (
        <LoadingState message="Loading analytical data..." />
      ) : error ? (
        <ErrorState message={error} onRetry={() => window.location.reload()} />
      ) : (
        <>
          {/* SECTION A: Dataset Overview */}
          <section className="space-y-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <span>1. Catalog Overview</span>
              </h2>
              <p className="text-xs text-neutral-400">
                Total record counts across movies, ratings, users, and genres
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                title="Total Movies"
                value={summary?.total_movies?.toLocaleString() ?? "2,500"}
                icon={Film}
                accentColor="indigo"
                subtitle="Catalog titles"
              />
              <StatCard
                title="Total Ratings"
                value={summary?.total_ratings?.toLocaleString() ?? "119,689"}
                icon={Star}
                accentColor="amber"
                subtitle="User reviews"
              />
              <StatCard
                title="Total Users"
                value={summary?.total_users?.toLocaleString() ?? "18,327"}
                icon={Users}
                accentColor="emerald"
                subtitle="Active reviewers"
              />
              <StatCard
                title="Distinct Genres"
                value={summary?.total_genres?.toLocaleString() ?? "16"}
                icon={Tags}
                accentColor="purple"
                subtitle="Taxonomy categories"
              />
            </div>
          </section>

          {/* SECTION B: Top-Rated Movies */}
          <section className="rounded-3xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/80 to-neutral-950/90 p-6 md:p-8 space-y-6 backdrop-blur-md shadow-xl shadow-black/40">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Star className="h-5 w-5 text-amber-400 fill-amber-400" />
                  <span>2. Top-Rated Movies Ranking</span>
                </h2>
                <p className="text-xs text-neutral-400 mt-0.5">
                  Filter movies by minimum rating count to discover top-rated titles
                </p>
              </div>

              {/* Threshold Filters */}
              <div className="flex flex-wrap items-center gap-3 text-xs">
                <div className="flex items-center gap-1.5 bg-neutral-900 p-1.5 rounded-lg border border-neutral-800">
                  <span className="text-neutral-400 pl-1">Min Ratings:</span>
                  {[5, 10, 25, 50].map((threshold) => (
                    <button
                      key={threshold}
                      type="button"
                      onClick={() => handleFilterTopRated(threshold, topRatedLimit)}
                      className={`px-2 py-0.5 rounded font-mono font-medium transition-colors ${
                        minRatings === threshold
                          ? "bg-indigo-600 text-white"
                          : "text-neutral-400 hover:text-white"
                      }`}
                    >
                      {threshold}
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-1.5 bg-neutral-900 p-1.5 rounded-lg border border-neutral-800">
                  <span className="text-neutral-400 pl-1">Limit:</span>
                  {[5, 10, 20].map((lim) => (
                    <button
                      key={lim}
                      type="button"
                      onClick={() => handleFilterTopRated(minRatings, lim)}
                      className={`px-2 py-0.5 rounded font-mono font-medium transition-colors ${
                        topRatedLimit === lim
                          ? "bg-indigo-600 text-white"
                          : "text-neutral-400 hover:text-white"
                      }`}
                    >
                      {lim}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Top-Rated Table */}
            {isTopRatedLoading ? (
              <div className="py-8">
                <LoadingState message="Scanning MonetDB rating columns with updated threshold..." />
              </div>
            ) : topMovies.length === 0 ? (
              <EmptyState
                title="No Movies Met Threshold"
                description={`No movies in the sample have at least ${minRatings} ratings. Try selecting a lower threshold.`}
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-neutral-950/80 text-neutral-400 uppercase font-semibold border-b border-neutral-800">
                    <tr>
                      <th className="py-3 px-4 w-12 text-center">Rank</th>
                      <th className="py-3 px-4">Movie Title</th>
                      <th className="py-3 px-4 w-28 text-center">Year</th>
                      <th className="py-3 px-4 w-32 text-right">Rating Count</th>
                      <th className="py-3 px-4 w-32 text-right">Avg Rating</th>
                      <th className="py-3 px-4 w-28 text-center">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-800/60 font-mono">
                    {topMovies.map((m, idx) => (
                      <tr
                        key={m.movie_id}
                        className="hover:bg-neutral-800/40 transition-colors"
                      >
                        <td className="py-3 px-4 text-center font-bold text-neutral-400">
                          #{idx + 1}
                        </td>
                        <td className="py-3 px-4 font-sans font-medium text-white">
                          <Link
                            href={`/movies/${m.movie_id}`}
                            className="hover:text-indigo-300 transition-colors line-clamp-1"
                          >
                            {m.title}
                          </Link>
                        </td>
                        <td className="py-3 px-4 text-center text-neutral-400">
                          {m.release_year ?? m.year ?? "N/A"}
                        </td>
                        <td className="py-3 px-4 text-right text-neutral-300">
                          {m.rating_count.toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-right font-bold text-amber-400">
                          <span className="inline-flex items-center gap-1">
                            <Star className="h-3 w-3 fill-amber-400" />
                            {(m.avg_rating ?? m.average_rating ?? 0).toFixed(2)}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center font-sans">
                          <Link
                            href={`/movies/${m.movie_id}`}
                            className="text-indigo-400 hover:text-indigo-300 text-xs font-semibold inline-flex items-center gap-0.5"
                          >
                            <span>Inspect</span>
                            <ArrowRight className="h-3 w-3" />
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* SECTION C & D: Genre Popularity & Rating Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Genre Popularity */}
            <section className="rounded-3xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/80 to-neutral-950/90 p-6 md:p-8 space-y-6 backdrop-blur-md shadow-xl shadow-black/40">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <Tags className="h-4 w-4 text-purple-400" />
                    <span>3. Genre Popularity</span>
                  </h2>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Total ratings and distribution across genres
                  </p>
                </div>

                <div className="flex items-center gap-1 bg-neutral-900 p-1 rounded-lg border border-neutral-800 text-xs">
                  <button
                    type="button"
                    onClick={() => setGenreView("chart")}
                    className={`p-1.5 rounded transition-colors ${
                      genreView === "chart" ? "bg-indigo-600 text-white" : "text-neutral-400 hover:text-white"
                    }`}
                    title="View as Bar Chart"
                  >
                    <BarChart2 className="h-3.5 w-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => setGenreView("table")}
                    className={`p-1.5 rounded transition-colors ${
                      genreView === "table" ? "bg-indigo-600 text-white" : "text-neutral-400 hover:text-white"
                    }`}
                    title="View as Accessible Data Table"
                  >
                    <TableIcon className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

              {genreView === "chart" ? (
                <div className="space-y-3 pt-2">
                  {genres.map((g) => {
                    const count = g.total_ratings ?? g.rating_count ?? 0;
                    const pct = Math.round((count / maxGenreCount) * 100);
                    return (
                      <div key={g.genre} className="space-y-1 text-xs">
                        <div className="flex items-center justify-between font-medium">
                          <span className="text-neutral-200">{g.genre}</span>
                          <span className="font-mono text-neutral-400">
                            {count.toLocaleString()} ratings
                          </span>
                        </div>
                        <div className="h-2.5 w-full rounded-full bg-neutral-800 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-indigo-500 transition-all duration-300"
                            style={{ width: `${pct}%` }}
                            role="progressbar"
                            aria-valuenow={count}
                            aria-valuemin={0}
                            aria-valuemax={maxGenreCount}
                            aria-label={`Genre ${g.genre} has ${count} ratings`}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-neutral-950 text-neutral-400 border-b border-neutral-800">
                      <tr>
                        <th className="py-2 px-3">Genre</th>
                        <th className="py-2 px-3 text-right">Rating Count</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-800">
                      {genres.map((g) => (
                        <tr key={g.genre} className="hover:bg-neutral-800/30">
                          <td className="py-2 px-3 font-sans font-medium text-white">{g.genre}</td>
                          <td className="py-2 px-3 text-right text-neutral-300">
                            {(g.total_ratings ?? g.rating_count ?? 0).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            {/* Rating Distribution Histogram */}
            <section className="rounded-3xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/80 to-neutral-950/90 p-6 md:p-8 space-y-6 backdrop-blur-md shadow-xl shadow-black/40">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-indigo-400" />
                    <span>4. Rating Distribution</span>
                  </h2>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Distribution of rating values (0.5 to 5.0 stars)
                  </p>
                </div>

                <div className="text-[11px] font-mono text-neutral-400 bg-neutral-950/80 px-2.5 py-1 rounded-full border border-neutral-800">
                  {totalDistributionRatings.toLocaleString()} total votes
                </div>
              </div>

              {/* Vertical Histogram Bars */}
              <div className="space-y-4 pt-2">
                <div className="flex items-end justify-between gap-1.5 h-44 pb-2 border-b border-neutral-800">
                  {distribution.map((item) => {
                    const heightPct = Math.max(
                      Math.round((item.count / maxDistributionCount) * 100),
                      4
                    );
                    const pctOfTotal =
                      totalDistributionRatings > 0
                        ? ((item.count / totalDistributionRatings) * 100).toFixed(1)
                        : "0.0";
                    return (
                      <div
                        key={item.rating}
                        className="flex-1 flex flex-col items-center gap-1 group relative h-full justify-end"
                      >
                        {/* Tooltip on hover */}
                        <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-neutral-950 text-white text-[10px] font-mono py-1 px-2 rounded border border-neutral-700 pointer-events-none z-10 whitespace-nowrap shadow-lg">
                          {item.count.toLocaleString()} ratings ({pctOfTotal}%)
                        </div>

                        {/* Bar */}
                        <div
                          className="w-full rounded-t-md bg-gradient-to-t from-indigo-600 to-indigo-400 group-hover:from-indigo-500 group-hover:to-indigo-300 transition-all duration-200"
                          style={{ height: `${heightPct}%` }}
                        />

                        {/* Star label */}
                        <span className="text-[10px] font-mono text-neutral-400 group-hover:text-white pt-1">
                          {item.rating.toFixed(1)}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* Accessible Text Summary Table */}
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-2 text-[11px] font-mono text-neutral-400">
                  {distribution.map((d) => (
                    <div
                      key={d.rating}
                      className="bg-neutral-950/80 p-2 rounded-lg border border-neutral-850 flex items-center justify-between"
                    >
                      <span className="text-amber-400 font-bold">{d.rating.toFixed(1)}★</span>
                      <span className="text-neutral-200">{d.count.toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>

          {/* SECTION E: Individual Movie Rating Analytics Deep Dive */}
          <section className="rounded-3xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/80 to-neutral-950/90 p-6 md:p-8 space-y-6 backdrop-blur-md shadow-xl shadow-black/40">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
              <div className="space-y-1">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Search className="h-4 w-4 text-emerald-400" />
                  <span>5. Individual Movie Rating Analytics</span>
                </h2>
                <p className="text-xs text-neutral-400">
                  Search and inspect detailed rating statistics for any movie by title
                </p>
              </div>

              <div className="w-full md:max-w-md">
                <MovieAutocomplete
                  selectedMovie={lookupMovie}
                  onSelectMovie={(movie) => {
                    setLookupMovie(movie);
                    fetchMovieAnalytics(movie);
                  }}
                  placeholder="Search movie by title (e.g. Tenet, Soul, Dune)..."
                />
              </div>
            </div>

            {isLookupLoading ? (
              <LoadingState message={`Calculating rating statistics for ${lookupMovie?.title || "selected movie"}...`} />
            ) : lookupError ? (
              <ErrorState title="Movie Not Found" message={lookupError} />
            ) : movieAnalytics ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
                <div className="rounded-2xl bg-neutral-950/80 border border-neutral-800/90 p-5 flex flex-col justify-between shadow-md">
                  <div>
                    <span className="text-xs text-neutral-400 font-medium">Selected Movie</span>
                    <div className="text-lg font-bold text-white mt-1 line-clamp-1" title={lookupMovie?.title}>
                      {lookupMovie?.title || `Movie #${movieAnalytics.movie_id}`}
                    </div>
                    {(lookupMovie?.year || lookupMovie?.release_year || (lookupMovie?.genres && lookupMovie.genres.length > 0)) && (
                      <div className="text-[11px] text-neutral-400 line-clamp-1 mt-0.5 font-mono">
                        {lookupMovie.year || lookupMovie.release_year ? `${lookupMovie.year || lookupMovie.release_year}` : ""}
                        {lookupMovie.genres && lookupMovie.genres.length > 0 ? ` • ${lookupMovie.genres.slice(0, 2).join(", ")}` : ""}
                      </div>
                    )}
                  </div>
                  <Link
                    href={`/movies/${movieAnalytics.movie_id}`}
                    className="text-indigo-400 hover:text-indigo-300 text-xs font-semibold inline-flex items-center gap-1.5 mt-3 transition-colors"
                  >
                    <span>View Movie Details</span>
                    <ArrowRight className="h-3 w-3" />
                  </Link>
                </div>

                <div className="rounded-2xl bg-neutral-950/80 border border-neutral-800/90 p-5 shadow-md">
                  <span className="text-xs text-neutral-400 font-medium">Average Rating</span>
                  <div className="text-2xl font-bold text-amber-400 font-mono mt-1.5 flex items-center gap-2">
                    <Star className="h-5 w-5 fill-amber-400 text-amber-400" />
                    <span>
                      {(movieAnalytics.avg_rating ?? movieAnalytics.average_rating) !== null &&
                      (movieAnalytics.avg_rating ?? movieAnalytics.average_rating) !== undefined
                        ? (movieAnalytics.avg_rating ?? movieAnalytics.average_rating)!.toFixed(2)
                        : "N/A"}
                    </span>
                  </div>
                  <span className="text-[11px] text-neutral-500 mt-0.5 block">out of 5.0 stars</span>
                </div>

                <div className="rounded-2xl bg-neutral-950/80 border border-neutral-800/90 p-5 shadow-md">
                  <span className="text-xs text-neutral-400 font-medium">Total Ratings</span>
                  <div className="text-2xl font-bold text-white font-mono mt-1.5">
                    {movieAnalytics.rating_count.toLocaleString()}
                  </div>
                  <span className="text-[11px] text-neutral-500 mt-0.5 block">total user ratings</span>
                </div>

                <div className="rounded-2xl bg-neutral-950/80 border border-neutral-800/90 p-5 shadow-md">
                  <span className="text-xs text-neutral-400 font-medium">Rating Range</span>
                  <div className="text-2xl font-bold text-neutral-200 font-mono mt-1.5">
                    {movieAnalytics.min_rating ?? "—"} - {movieAnalytics.max_rating ?? "—"}
                  </div>
                  <span className="text-[11px] text-neutral-500 mt-0.5 block">min - max scale</span>
                </div>
              </div>
            ) : null}
          </section>
        </>
      )}
    </div>
  );
}
