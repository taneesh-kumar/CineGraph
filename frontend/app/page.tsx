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
  CheckCircle2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { DatasetSummary, TopRatedMovie, GenrePopularity, ReadinessResponse } from "@/lib/types";
import { StatCard } from "@/components/ui/StatCard";
import { EngineBadge } from "@/components/ui/EngineBadge";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";

export default function OverviewPage() {
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [topMovies, setTopMovies] = useState<TopRatedMovie[]>([]);
  const [genres, setGenres] = useState<GenrePopularity[]>([]);
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sumRes, topRes, genRes, readyRes] = await Promise.allSettled([
        apiClient.getDatasetSummary(),
        apiClient.getTopRatedMovies(10, 4),
        apiClient.getGenrePopularity(5),
        apiClient.getReadiness(),
      ]);

      if (sumRes.status === "fulfilled") setSummary(sumRes.value);
      if (topRes.status === "fulfilled") setTopMovies(topRes.value);
      if (genRes.status === "fulfilled") setGenres(genRes.value);
      if (readyRes.status === "fulfilled") setReadiness(readyRes.value);

      if (sumRes.status === "rejected" && readyRes.status === "rejected") {
        throw new Error(
          "Unable to connect to CineGraph backend. Please ensure FastAPI (:8000), Neo4j (:7687) and MonetDB (:50000) are running."
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
      <section className="relative overflow-hidden rounded-2xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/80 via-neutral-900/40 to-neutral-950 p-8 sm:p-12">
        <div className="max-w-3xl space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-indigo-400">
              <Sparkles className="h-3 w-3" />
              Academic NoSQL Demonstration
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-300">
              MovieLens 32M Sample (2020–2023)
            </span>
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-5xl leading-tight">
            Graph Recommendations &{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-rose-400 to-amber-400">
              Columnar Analytics
            </span>
          </h1>

          <p className="text-base sm:text-lg text-neutral-300 leading-relaxed">
            CineGraph evaluates complementary NoSQL database paradigms side-by-side.{" "}
            <strong className="text-white">Neo4j</strong> models movie relationship topology,
            genre graphs, and collaborative recommendation walks.{" "}
            <strong className="text-white">MonetDB</strong> executes high-speed columnar
            aggregations and OLAP rating distribution benchmarks across millions of entries.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link
              href="/movies"
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-600/30 hover:bg-indigo-500 transition-colors"
            >
              <Film className="h-4 w-4" />
              <span>Explore Movies</span>
            </Link>
            <Link
              href="/recommendations"
              className="inline-flex items-center gap-2 rounded-xl border border-neutral-700 bg-neutral-900/80 px-5 py-2.5 text-sm font-semibold text-neutral-200 hover:border-neutral-600 hover:bg-neutral-800 transition-colors"
            >
              <Sparkles className="h-4 w-4 text-indigo-400" />
              <span>Graph Recommendations</span>
            </Link>
            <Link
              href="/analytics"
              className="inline-flex items-center gap-2 rounded-xl border border-neutral-700 bg-neutral-900/80 px-5 py-2.5 text-sm font-semibold text-neutral-200 hover:border-neutral-600 hover:bg-neutral-800 transition-colors"
            >
              <BarChart3 className="h-4 w-4 text-emerald-400" />
              <span>Columnar Analytics</span>
            </Link>
          </div>
        </div>

        {/* Readiness Pill */}
        <div className="mt-8 pt-6 border-t border-neutral-800/80 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2 text-neutral-400">
            {readiness?.status === "ready" ? (
              <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                Backend Dual-Engines Ready
              </span>
            ) : readiness ? (
              <span className="flex items-center gap-1.5 text-amber-400 font-medium">
                <AlertCircle className="h-4 w-4 text-amber-400" />
                Degraded Engine Status ({readiness.status})
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-neutral-500">
                <AlertCircle className="h-4 w-4 text-neutral-500" />
                Probing Backend Readiness...
              </span>
            )}
            <span className="text-neutral-600">•</span>
            <span className="font-mono text-neutral-400">
              Neo4j: {readiness?.neo4j?.status === "connected" ? "Online (Bolt)" : "Connecting"} |
              MonetDB: {readiness?.monetdb?.status === "connected" ? "Online (MAPI)" : "Connecting"}
            </span>
          </div>

          <button
            onClick={loadData}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-800 bg-neutral-900 px-3 py-1 text-neutral-300 hover:border-neutral-700 hover:text-white transition-colors disabled:opacity-50"
            title="Refresh overview metrics"
          >
            <RefreshCw className={`h-3 w-3 ${isLoading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>
      </section>

      {/* Dataset Summary Metrics */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="h-5 w-5 text-indigo-400" />
              Dataset Statistics
            </h2>
            <p className="text-xs text-neutral-400">
              Live counts from MonetDB analytical catalog for current development sample
            </p>
          </div>
          <EngineBadge engine="monetdb" />
        </div>

        {isLoading && !summary ? (
          <LoadingState message="Aggregating dataset catalog from MonetDB..." />
        ) : error && !summary ? (
          <ErrorState message={error} onRetry={loadData} />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              title="Ingested Movies"
              value={summary?.total_movies?.toLocaleString() ?? "2,500"}
              subtitle="2020–2023 Sample"
              icon={Film}
              engine="monetdb"
            />
            <StatCard
              title="Total Ratings"
              value={summary?.total_ratings?.toLocaleString() ?? "119,689"}
              subtitle="Analytical Fact Table"
              icon={Star}
              engine="monetdb"
            />
            <StatCard
              title="Active Users"
              value={summary?.total_users?.toLocaleString() ?? "18,327"}
              subtitle="User Rating Graph"
              icon={Users}
              engine="neo4j"
            />
            <StatCard
              title="Movie Genres"
              value={summary?.total_genres?.toLocaleString() ?? "16"}
              subtitle="Graph Dimension Nodes"
              icon={Tags}
              engine="hybrid"
            />
          </div>
        )}
      </section>

      {/* Architecture Showcase: Neo4j vs MonetDB */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg font-bold text-white">Dual NoSQL Architecture Breakdown</h2>
          <p className="text-xs text-neutral-400">
            Engine specialization and verified query execution patterns
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Neo4j Card */}
          <div className="rounded-2xl border border-indigo-900/40 bg-neutral-900/60 p-6 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                    <Database className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base">Neo4j Community Graph</h3>
                    <span className="text-xs text-neutral-400 font-mono">Port 7687 (Bolt Driver)</span>
                  </div>
                </div>
                <EngineBadge engine="neo4j" />
              </div>

              <p className="text-sm text-neutral-300 leading-relaxed">
                Stores movies, genres, and user rating relationships as an interconnected graph.
                Excels at relationship walks, Jaccard content similarity, and collaborative filtering
                via co-rating traversals without expensive relational joins.
              </p>

              <div className="mt-4 rounded-lg border border-neutral-800 bg-neutral-950 p-3 font-mono text-xs text-indigo-300/90 overflow-x-auto">
                <code>
                  MATCH (m:Movie &#123;id: $id&#125;)-[:HAS_GENRE]-&gt;(g:Genre)&lt;-[:HAS_GENRE]-(rec:Movie)<br />
                  RETURN rec.title, count(g) AS shared_genres
                </code>
              </div>
            </div>

            <div className="pt-4 border-t border-neutral-800/80 flex items-center justify-between text-xs">
              <span className="text-neutral-400">Serves: Recommendations API</span>
              <Link
                href="/recommendations"
                className="inline-flex items-center gap-1 font-semibold text-indigo-400 hover:text-indigo-300"
              >
                <span>Test Graph Walk</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>

          {/* MonetDB Card */}
          <div className="rounded-2xl border border-emerald-900/40 bg-neutral-900/60 p-6 flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                    <Cpu className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-base">MonetDB Analytical Column-Store</h3>
                    <span className="text-xs text-neutral-400 font-mono">Port 50000 (MAPI Protocol)</span>
                  </div>
                </div>
                <EngineBadge engine="monetdb" />
              </div>

              <p className="text-sm text-neutral-300 leading-relaxed">
                Stores movies, ratings, and tags in vertical, column-vector representations.
                Excels at vectorized scans, grouped aggregations, top-rated thresholds, and
                distribution histograms across millions of rating tuples in milliseconds.
              </p>

              <div className="mt-4 rounded-lg border border-neutral-800 bg-neutral-950 p-3 font-mono text-xs text-emerald-300/90 overflow-x-auto">
                <code>
                  SELECT m.title, AVG(r.rating) AS avg_score, COUNT(r.rating) AS n<br />
                  FROM ratings r JOIN movies m ON r.movie_id = m.movie_id<br />
                  GROUP BY m.title HAVING COUNT(r.rating) &gt;= 10
                </code>
              </div>
            </div>

            <div className="pt-4 border-t border-neutral-800/80 flex items-center justify-between text-xs">
              <span className="text-neutral-400">Serves: Analytics API</span>
              <Link
                href="/analytics"
                className="inline-flex items-center gap-1 font-semibold text-emerald-400 hover:text-emerald-300"
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
        <section className="rounded-2xl border border-neutral-800/80 bg-neutral-900/40 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Star className="h-4 w-4 text-amber-400" />
                Top-Rated Movies Preview
              </h2>
              <p className="text-xs text-neutral-400">Min. 10 ratings required (MonetDB scan)</p>
            </div>
            <Link
              href="/analytics"
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
            >
              <span>Full Table</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>

          {topMovies.length > 0 ? (
            <div className="space-y-2.5">
              {topMovies.map((movie, idx) => (
                <div
                  key={movie.movie_id}
                  className="flex items-center justify-between p-3 rounded-xl border border-neutral-800 bg-neutral-900/80 text-xs"
                >
                  <div className="flex items-center gap-3">
                    <span className="flex h-6 w-6 items-center justify-center rounded-md bg-neutral-800 font-mono font-bold text-neutral-300">
                      {idx + 1}
                    </span>
                    <div>
                      <Link
                        href={`/movies/${movie.movie_id}`}
                        className="font-medium text-white hover:text-indigo-300 transition-colors line-clamp-1"
                      >
                        {movie.title}
                      </Link>
                      <span className="text-[11px] text-neutral-500 font-mono">
                        {movie.rating_count.toLocaleString()} ratings
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 font-bold text-amber-400 bg-amber-400/10 px-2.5 py-1 rounded-md border border-amber-400/20">
                    <Star className="h-3.5 w-3.5 fill-amber-400" />
                    <span>{(movie.avg_rating ?? movie.average_rating ?? 0).toFixed(2)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-6 text-center text-xs text-neutral-500">
              No top-rated preview available.
            </div>
          )}
        </section>

        {/* Genre Popularity Preview */}
        <section className="rounded-2xl border border-neutral-800/80 bg-neutral-900/40 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Tags className="h-4 w-4 text-emerald-400" />
                Popular Genres Preview
              </h2>
              <p className="text-xs text-neutral-400">Total ratings by genre from MonetDB</p>
            </div>
            <Link
              href="/analytics"
              className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
            >
              <span>View Chart</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>

          {genres.length > 0 ? (
            <div className="space-y-3">
              {genres.map((g) => {
                const count = g.total_ratings ?? g.rating_count ?? 0;
                const maxRatings = genres[0]?.total_ratings ?? genres[0]?.rating_count ?? 1;
                const pct = Math.round((count / maxRatings) * 100);
                return (
                  <div key={g.genre} className="space-y-1 text-xs">
                    <div className="flex items-center justify-between font-medium">
                      <span className="text-neutral-200">{g.genre}</span>
                      <span className="text-neutral-400 font-mono">
                        {count.toLocaleString()} ratings
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-neutral-800 overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-indigo-500"
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
