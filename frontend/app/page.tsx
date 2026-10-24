"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Film,
  Users,
  Star,
  Tags,
  Sparkles,
  BarChart3,
  ArrowRight,
  Database,
  Cpu,
  Layers,
  RefreshCw,
  GitBranch,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { DatasetSummary, TopRatedMovie, GenrePopularity } from "@/lib/types";
import { StatCard } from "@/components/ui/StatCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";

export default function OverviewPage() {
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [topMovies, setTopMovies] = useState<TopRatedMovie[]>([]);
  const [genres, setGenres] = useState<GenrePopularity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sumRes, topRes, genRes] = await Promise.allSettled([
        apiClient.getDatasetSummary(),
        apiClient.getTopRatedMovies(10, 4),
        apiClient.getGenrePopularity(5),
      ]);

      if (sumRes.status === "fulfilled") setSummary(sumRes.value);
      if (topRes.status === "fulfilled") setTopMovies(topRes.value);
      if (genRes.status === "fulfilled") setGenres(genRes.value);

      if (sumRes.status === "rejected") {
        throw new Error(
          "Unable to connect to CineGraph backend. Please ensure the backend server is running."
        );
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load overview data";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl border border-neutral-800/80 bg-gradient-to-br from-neutral-900/90 via-neutral-950 to-neutral-950 p-8 sm:p-12 shadow-2xl backdrop-blur-xl">
        {/* Ambient interior glow */}
        <div className="absolute top-0 right-1/4 -mt-16 h-72 w-72 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-10 h-64 w-64 rounded-full bg-purple-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          {/* Hero Left Copy */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3.5 py-1 text-xs font-semibold text-indigo-300 shadow-sm shadow-indigo-500/10 backdrop-blur-md">
              <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
              <span>Interactive Graph Discovery & Columnar Analytics</span>
            </div>

            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-5xl leading-tight">
              Movie Recommendations &{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-300 to-amber-300">
                Graph Analytics
              </span>
            </h1>

            <p className="text-base sm:text-lg text-neutral-300 leading-relaxed max-w-2xl">
              Explore interconnected movie universes, discover similarity walks across shared genres and community co-ratings, and analyze deep distribution trends in real time.
            </p>

            <div className="flex flex-wrap items-center gap-3 pt-1">
              <Link
                href="/movies"
                className="inline-flex items-center gap-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 hover:from-indigo-500 hover:to-indigo-400 hover:shadow-indigo-500/40 transition-all duration-200"
              >
                <Film className="h-4 w-4" />
                <span>Explore Movies</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/recommendations"
                className="inline-flex items-center gap-2 rounded-xl border border-neutral-700/80 bg-neutral-900/80 px-5 py-3 text-sm font-semibold text-neutral-200 hover:border-neutral-600 hover:bg-neutral-800 hover:text-white transition-all shadow-sm"
              >
                <Sparkles className="h-4 w-4 text-indigo-400" />
                <span>Recommendations</span>
              </Link>
              <Link
                href="/analytics"
                className="inline-flex items-center gap-2 rounded-xl border border-neutral-700/80 bg-neutral-900/80 px-5 py-3 text-sm font-semibold text-neutral-200 hover:border-neutral-600 hover:bg-neutral-800 hover:text-white transition-all shadow-sm"
              >
                <BarChart3 className="h-4 w-4 text-emerald-400" />
                <span>Analytics</span>
              </Link>
            </div>
          </div>

          {/* Hero Right Visual: Connected Movie Graph Showcase Card */}
          <div className="lg:col-span-5 hidden lg:block">
            <div className="relative rounded-2xl border border-neutral-800 bg-neutral-900/70 p-5 shadow-2xl backdrop-blur-md space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-neutral-800/80 text-xs">
                <span className="font-semibold text-neutral-300 flex items-center gap-1.5">
                  <GitBranch className="h-3.5 w-3.5 text-indigo-400" />
                  Live Graph Walk Preview
                </span>
                <span className="rounded bg-indigo-500/10 px-2 py-0.5 text-[10px] font-mono font-medium text-indigo-300 border border-indigo-500/20">
                  Jaccard Similarity
                </span>
              </div>

              {/* Source Movie */}
              <div className="rounded-xl border border-neutral-800 bg-neutral-950/90 p-3.5 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-white text-sm">Tenet (2020)</span>
                  <div className="flex items-center gap-1 font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20 text-xs">
                    <Star className="h-3 w-3 fill-amber-400" />
                    <span>4.30</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1 text-[10px]">
                  <span className="rounded bg-neutral-800 px-2 py-0.5 text-neutral-300">Action</span>
                  <span className="rounded bg-neutral-800 px-2 py-0.5 text-neutral-300">Sci-Fi</span>
                  <span className="rounded bg-neutral-800 px-2 py-0.5 text-neutral-300">Thriller</span>
                </div>
              </div>

              {/* Connector line with node weight */}
              <div className="flex items-center justify-center gap-2 text-[11px] text-neutral-500 font-mono py-0.5">
                <div className="h-[1px] flex-1 bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />
                <span className="px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800/60 font-semibold text-[10px]">
                  Shared Genre Node Link
                </span>
                <div className="h-[1px] flex-1 bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />
              </div>

              {/* Target Recommendation Candidate */}
              <div className="rounded-xl border border-indigo-900/60 bg-gradient-to-r from-indigo-950/40 to-neutral-950/80 p-3.5 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <div>
                    <span className="font-bold text-white text-sm">Soul (2020)</span>
                    <span className="text-[10px] text-neutral-400 ml-2">Score: 0.850</span>
                  </div>
                  <div className="flex items-center gap-1 font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20 text-xs">
                    <Star className="h-3 w-3 fill-amber-400" />
                    <span>4.15</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1 text-[10px]">
                  <span className="rounded bg-neutral-800/90 px-2 py-0.5 text-neutral-300">Animation</span>
                  <span className="rounded bg-neutral-800/90 px-2 py-0.5 text-neutral-300">Fantasy</span>
                  <span className="rounded bg-neutral-800/90 px-2 py-0.5 text-neutral-300">Comedy</span>
                </div>
              </div>

              <div className="pt-2 text-right">
                <Link
                  href="/recommendations?movie_id=217465"
                  className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  <span>Explore in Graph Engine</span>
                  <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Dataset Summary Metrics */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2.5">
              <Layers className="h-5 w-5 text-indigo-400" />
              Dataset Statistics
            </h2>
            <p className="text-xs text-neutral-400 mt-0.5">
              Overview of catalog movies, ratings, users, and genres
            </p>
          </div>
          <button
            onClick={loadData}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 rounded-xl border border-neutral-800 bg-neutral-900/90 px-3.5 py-1.5 text-xs text-neutral-300 hover:border-neutral-700 hover:text-white hover:bg-neutral-850 transition-all disabled:opacity-50 shadow-sm"
            title="Refresh statistics"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin text-indigo-400" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>

        {isLoading && !summary ? (
          <LoadingState message="Loading catalog statistics..." />
        ) : error && !summary ? (
          <ErrorState message={error} onRetry={loadData} />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              title="Total Movies"
              value={summary?.total_movies?.toLocaleString() ?? "2,500"}
              subtitle="Curated 2020–2023 catalog"
              icon={Film}
              accentColor="indigo"
            />
            <StatCard
              title="Total Ratings"
              value={summary?.total_ratings?.toLocaleString() ?? "119,689"}
              subtitle="Verified user reviews"
              icon={Star}
              accentColor="amber"
            />
            <StatCard
              title="Active Users"
              value={summary?.total_users?.toLocaleString() ?? "18,327"}
              subtitle="Community taste profiles"
              icon={Users}
              accentColor="emerald"
            />
            <StatCard
              title="Movie Genres"
              value={summary?.total_genres?.toLocaleString() ?? "16"}
              subtitle="Categorical dimensions"
              icon={Tags}
              accentColor="purple"
            />
          </div>
        )}
      </section>

      {/* Dual Database Architecture Showcase */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-white">Dual Database Architecture</h2>
          <p className="text-xs text-neutral-400 mt-0.5">
            Specialized engines optimized for graph walks and columnar analytics
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Neo4j Card */}
          <div className="group rounded-3xl border border-neutral-800 bg-gradient-to-b from-neutral-900/90 to-neutral-950 p-6 flex flex-col justify-between space-y-5 hover:border-indigo-500/40 hover:shadow-2xl hover:shadow-indigo-950/20 transition-all duration-300">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-sm shadow-indigo-500/20">
                    <Database className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base">Neo4j Graph Database</h3>
                    <span className="text-xs text-indigo-400/90 font-mono">Graph Traversal & Relationships</span>
                  </div>
                </div>
              </div>

              <p className="text-sm text-neutral-300 leading-relaxed">
                Stores movies, genres, and user rating relationships as an interconnected graph.
                Excels at relationship walks, Jaccard content similarity, and collaborative filtering
                via co-rating traversals without expensive relational joins.
              </p>

              {/* Stylized Cypher Block */}
              <div className="rounded-xl border border-neutral-800/90 bg-neutral-950 p-3.5 font-mono text-xs overflow-x-auto shadow-inner">
                <div className="flex items-center justify-between text-[11px] text-neutral-500 pb-2 mb-2 border-b border-neutral-850">
                  <span>Cypher Pattern Match</span>
                  <span className="text-indigo-400">Port 7687 • Bolt</span>
                </div>
                <code className="text-neutral-300">
                  <span className="text-purple-400">MATCH</span> (m:Movie &#123;id: $id&#125;)-[:HAS_GENRE]-&gt;(g:Genre)&lt;-[:HAS_GENRE]-(rec:Movie)<br />
                  <span className="text-purple-400">RETURN</span> rec.title, <span className="text-amber-400">count</span>(g) <span className="text-purple-400">AS</span> shared_genres
                </code>
              </div>
            </div>

            <div className="pt-4 border-t border-neutral-800/80 flex items-center justify-between text-xs">
              <span className="text-neutral-400 font-medium">Powers: Recommendations Engine</span>
              <Link
                href="/recommendations"
                className="inline-flex items-center gap-1.5 font-semibold text-indigo-400 hover:text-indigo-300 group-hover:translate-x-0.5 transition-all"
              >
                <span>View Recommendations</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>

          {/* MonetDB Card */}
          <div className="group rounded-3xl border border-neutral-800 bg-gradient-to-b from-neutral-900/90 to-neutral-950 p-6 flex flex-col justify-between space-y-5 hover:border-emerald-500/40 hover:shadow-2xl hover:shadow-emerald-950/20 transition-all duration-300">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-sm shadow-emerald-500/20">
                    <Cpu className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base">MonetDB Column-Store</h3>
                    <span className="text-xs text-emerald-400/90 font-mono">Fast Aggregations & OLAP</span>
                  </div>
                </div>
              </div>

              <p className="text-sm text-neutral-300 leading-relaxed">
                Stores movies, ratings, and tags in vertical column-vector representations.
                Excels at vectorized scans, grouped aggregations, top-rated thresholds, and
                distribution histograms across millions of rating tuples in milliseconds.
              </p>

              {/* Stylized SQL Block */}
              <div className="rounded-xl border border-neutral-800/90 bg-neutral-950 p-3.5 font-mono text-xs overflow-x-auto shadow-inner">
                <div className="flex items-center justify-between text-[11px] text-neutral-500 pb-2 mb-2 border-b border-neutral-850">
                  <span>Vectorized SQL Aggregation</span>
                  <span className="text-emerald-400">Port 50000 • MAPI</span>
                </div>
                <code className="text-neutral-300">
                  <span className="text-purple-400">SELECT</span> m.title, <span className="text-amber-400">AVG</span>(r.rating) <span className="text-purple-400">AS</span> avg_score, <span className="text-amber-400">COUNT</span>(r.rating) <span className="text-purple-400">AS</span> n<br />
                  <span className="text-purple-400">FROM</span> ratings r <span className="text-purple-400">JOIN</span> movies m <span className="text-purple-400">ON</span> r.movie_id = m.movie_id<br />
                  <span className="text-purple-400">GROUP BY</span> m.title <span className="text-purple-400">HAVING</span> <span className="text-amber-400">COUNT</span>(r.rating) &gt;= 10
                </code>
              </div>
            </div>

            <div className="pt-4 border-t border-neutral-800/80 flex items-center justify-between text-xs">
              <span className="text-neutral-400 font-medium">Powers: Analytics Dashboard</span>
              <Link
                href="/analytics"
                className="inline-flex items-center gap-1.5 font-semibold text-emerald-400 hover:text-emerald-300 group-hover:translate-x-0.5 transition-all"
              >
                <span>View Analytics</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Top-Rated Movies & Genre Previews */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top-Rated Preview */}
        <section className="rounded-3xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/60 to-neutral-950 p-6 space-y-4 backdrop-blur-md shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Star className="h-4 w-4 text-amber-400 fill-amber-400/20" />
                Top-Rated Movies Preview
              </h2>
              <p className="text-xs text-neutral-400">Min. 10 ratings required</p>
            </div>
            <Link
              href="/analytics"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 transition-colors"
            >
              <span>Full Table</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          {topMovies.length > 0 ? (
            <div className="space-y-2.5">
              {topMovies.map((movie, idx) => {
                const medalColors = [
                  "bg-amber-500/20 text-amber-300 border-amber-500/30",
                  "bg-neutral-300/20 text-neutral-200 border-neutral-400/30",
                  "bg-amber-700/20 text-amber-500 border-amber-700/30",
                ];
                const badgeStyle = medalColors[idx] || "bg-neutral-800 text-neutral-400 border-neutral-700";

                return (
                  <div
                    key={movie.movie_id}
                    className="flex items-center justify-between p-3 rounded-2xl border border-neutral-800/80 bg-neutral-900/60 hover:bg-neutral-850 hover:border-neutral-700 text-xs transition-all duration-200 group"
                  >
                    <div className="flex items-center gap-3 min-w-0 pr-3">
                      <span className={`flex h-6 w-6 items-center justify-center rounded-lg border font-mono font-bold text-xs shrink-0 ${badgeStyle}`}>
                        {idx + 1}
                      </span>
                      <div className="truncate">
                        <Link
                          href={`/movies/${movie.movie_id}`}
                          className="font-semibold text-white group-hover:text-indigo-300 transition-colors truncate block"
                        >
                          {movie.title}
                        </Link>
                        <span className="text-[11px] text-neutral-500 font-mono">
                          {movie.rating_count.toLocaleString()} ratings
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 font-bold text-amber-400 bg-amber-400/10 px-2.5 py-1 rounded-lg border border-amber-400/20 shrink-0">
                      <Star className="h-3.5 w-3.5 fill-amber-400" />
                      <span>{(movie.avg_rating ?? movie.average_rating ?? 0).toFixed(2)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-6 text-center text-xs text-neutral-500">
              No top-rated preview available.
            </div>
          )}
        </section>

        {/* Genre Popularity Preview */}
        <section className="rounded-3xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/60 to-neutral-950 p-6 space-y-4 backdrop-blur-md shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Tags className="h-4 w-4 text-emerald-400" />
                Popular Genres Preview
              </h2>
              <p className="text-xs text-neutral-400">Total ratings by genre</p>
            </div>
            <Link
              href="/analytics"
              className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 transition-colors"
            >
              <span>View Chart</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          {genres.length > 0 ? (
            <div className="space-y-3.5 pt-1">
              {genres.map((g) => {
                const count = g.total_ratings ?? g.rating_count ?? 0;
                const maxRatings = genres[0]?.total_ratings ?? genres[0]?.rating_count ?? 1;
                const pct = Math.round((count / maxRatings) * 100);
                return (
                  <div key={g.genre} className="space-y-1.5 text-xs group">
                    <div className="flex items-center justify-between font-medium">
                      <span className="text-neutral-200 group-hover:text-white transition-colors">{g.genre}</span>
                      <span className="text-neutral-400 font-mono text-[11px]">
                        {count.toLocaleString()} ratings
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-neutral-800/80 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 transition-all duration-300"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-6 text-center text-xs text-neutral-500">
              No genre preview available.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
