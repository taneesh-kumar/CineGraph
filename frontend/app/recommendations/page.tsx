"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Sparkles,
  Users,
  Film,
  ArrowRight,
  Sliders,
  CheckCircle2,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { RecommendationResult, RecommendationItem } from "@/lib/types";
import { EngineBadge } from "@/components/ui/EngineBadge";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";

const SAMPLE_MOVIES = [
  { id: 217465, title: "Tenet (2020)" },
  { id: 225173, title: "Soul (2020)" },
  { id: 210861, title: "The Gentlemen (2020)" },
  { id: 218537, title: "Palm Springs (2020)" },
  { id: 219994, title: "The Father (2020)" },
];

const SAMPLE_USERS = [
  { id: 57304, label: "User #57304 (368 ratings)" },
  { id: 139018, label: "User #139018 (339 ratings)" },
  { id: 8901, label: "User #8901 (337 ratings)" },
  { id: 8359, label: "User #8359 (203 ratings)" },
];

function RecommendationsContent() {
  const searchParams = useSearchParams();
  const initialMovieParam = searchParams.get("movie_id");

  const [mode, setMode] = useState<"movie" | "user">("movie");
  const [movieIdInput, setMovieIdInput] = useState(initialMovieParam || "1");
  const [userIdInput, setUserIdInput] = useState("1");
  const [limit, setLimit] = useState(10);

  const [results, setResults] = useState<RecommendationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeRecommendation = async (
    targetMode: "movie" | "user",
    id: number,
    lim: number
  ) => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    try {
      if (targetMode === "movie") {
        const data = await apiClient.getMovieRecommendations(id, lim);
        setResults(data);
      } else {
        const data = await apiClient.getUserRecommendations(id, lim);
        setResults(data);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to fetch recommendations";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  // Run automatically on first mount if movie_id query param was passed
  useEffect(() => {
    if (initialMovieParam) {
      const parsed = parseInt(initialMovieParam, 10);
      if (!isNaN(parsed) && parsed > 0) {
        setMovieIdInput(initialMovieParam);
        setMode("movie");
        executeRecommendation("movie", parsed, limit);
      }
    } else {
      // Run default recommendation (Tenet)
      executeRecommendation("movie", 217465, 10);
    }
  }, [initialMovieParam]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (mode === "movie") {
      const id = parseInt(movieIdInput, 10);
      if (isNaN(id) || id <= 0) {
        setError("Please enter a valid positive Movie ID.");
        return;
      }
      executeRecommendation("movie", id, limit);
    } else {
      const id = parseInt(userIdInput, 10);
      if (isNaN(id) || id <= 0) {
        setError("Please enter a valid positive User ID.");
        return;
      }
      executeRecommendation("user", id, limit);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-indigo-400" />
              Recommendation Engine
            </h1>
            <EngineBadge engine="neo4j" />
          </div>
          <p className="text-sm text-neutral-400 mt-1">
            Traverse Neo4j Cypher graph relationships using Jaccard content similarity and collaborative community walks.
          </p>
        </div>

        <div className="inline-flex rounded-xl bg-neutral-900 p-1 border border-neutral-800">
          <button
            type="button"
            onClick={() => {
              setMode("movie");
              setResults(null);
              setError(null);
            }}
            className={`flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
              mode === "movie"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            <Film className="h-3.5 w-3.5" />
            <span>Similar Movies (Item)</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("user");
              setResults(null);
              setError(null);
            }}
            className={`flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
              mode === "user"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            <Users className="h-3.5 w-3.5" />
            <span>Personalized (User)</span>
          </button>
        </div>
      </div>

      {/* Control Box */}
      <div className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-6 space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div className="md:col-span-2 space-y-1.5">
              <label className="text-xs font-semibold text-neutral-300 flex items-center justify-between">
                <span>{mode === "movie" ? "MovieLens Movie ID" : "MovieLens User ID"}</span>
                <span className="text-[11px] text-neutral-500 font-normal">
                  {mode === "movie" ? "Integer (1 - 1000 in sample)" : "Integer (1 - 2364 in sample)"}
                </span>
              </label>
              <input
                type="number"
                min="1"
                value={mode === "movie" ? movieIdInput : userIdInput}
                onChange={(e) =>
                  mode === "movie"
                    ? setMovieIdInput(e.target.value)
                    : setUserIdInput(e.target.value)
                }
                placeholder={mode === "movie" ? "e.g. 1" : "e.g. 42"}
                className="w-full rounded-xl border border-neutral-800 bg-neutral-950 px-3.5 py-2.5 text-sm text-white placeholder:text-neutral-600 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-neutral-300 flex items-center gap-1.5">
                <Sliders className="h-3 w-3" />
                <span>Limit</span>
              </label>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="w-full rounded-xl border border-neutral-800 bg-neutral-950 px-3 py-2.5 text-sm text-white focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value={5}>Top 5</option>
                <option value={10}>Top 10</option>
                <option value={15}>Top 15</option>
                <option value={20}>Top 20</option>
              </select>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-600/30 transition-colors flex items-center justify-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                <span>{isLoading ? "Traversing..." : "Run Recommendation"}</span>
              </button>
            </div>
          </div>
        </form>

        {/* Example Quick-Pick Chips */}
        <div className="flex flex-wrap items-center gap-2 text-xs pt-2 border-t border-neutral-800/80">
          <span className="text-neutral-500">Quick Samples:</span>
          {mode === "movie"
            ? SAMPLE_MOVIES.map((sample) => (
                <button
                  key={sample.id}
                  type="button"
                  onClick={() => {
                    setMovieIdInput(String(sample.id));
                    executeRecommendation("movie", sample.id, limit);
                  }}
                  className="rounded-md border border-neutral-800 bg-neutral-900/80 px-2.5 py-1 text-neutral-300 hover:border-neutral-700 hover:text-white transition-colors"
                >
                  {sample.title}
                </button>
              ))
            : SAMPLE_USERS.map((sample) => (
                <button
                  key={sample.id}
                  type="button"
                  onClick={() => {
                    setUserIdInput(String(sample.id));
                    executeRecommendation("user", sample.id, limit);
                  }}
                  className="rounded-md border border-neutral-800 bg-neutral-900/80 px-2.5 py-1 text-neutral-300 hover:border-neutral-700 hover:text-white transition-colors"
                >
                  {sample.label}
                </button>
              ))}
        </div>
      </div>

      {/* Results Section */}
      {isLoading ? (
        <LoadingState
          message={`Executing ${
            mode === "movie" ? "Jaccard similarity walk" : "collaborative filtering graph traversal"
          } in Neo4j...`}
        />
      ) : error ? (
        <ErrorState message={error} onRetry={handleSubmit} />
      ) : results ? (
        <div className="space-y-6">
          {/* Metadata Banner */}
          <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <div>
                <span className="font-semibold text-white">
                  {(results.source_type || results.target_type) === "movie"
                    ? `Recommendations for Movie #${results.source_id || results.target_id}${results.source_title ? `: ${results.source_title}` : ""}`
                    : `Personalized Recommendations for User #${results.source_id || results.target_id}`}
                </span>
                <p className="text-neutral-400 text-[11px]">
                  Algorithm:{" "}
                  <span className="font-mono text-indigo-300">
                    {results.algorithm ||
                      ((results.source_type || results.target_type) === "movie"
                        ? "Jaccard Content Similarity"
                        : "Collaborative Filtering Graph Traversal")}
                  </span>
                </p>
              </div>
            </div>

            <div className="text-neutral-500 font-mono text-[11px]">
              Returned {results.recommendations.length} ranked candidate(s)
            </div>
          </div>

          {/* Cards Grid */}
          {results.recommendations.length === 0 ? (
            <EmptyState
              title="No Recommendations Found"
              description={
                mode === "movie"
                  ? "No neighboring movies met the similarity threshold in the graph sample."
                  : "This user may not have enough rating connections in the development sample to produce collaborative candidates."
              }
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.recommendations.map((rec: RecommendationItem, index: number) => (
                <div
                  key={rec.movie_id}
                  className="flex flex-col justify-between rounded-xl border border-neutral-800/90 bg-neutral-900/70 p-5 shadow-sm hover:border-neutral-700 hover:bg-neutral-900 transition-all"
                >
                  <div>
                    {/* Header rank & score */}
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="flex h-5 w-5 items-center justify-center rounded-md bg-neutral-800 font-mono text-[11px] font-bold text-neutral-300">
                        {index + 1}
                      </span>
                      <div className="flex items-center gap-1 font-mono text-xs font-bold text-indigo-400 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-800/60">
                        <span>Score:</span>
                        <span>{rec.score.toFixed(3)}</span>
                      </div>
                    </div>

                    {/* Title */}
                    <Link
                      href={`/movies/${rec.movie_id}`}
                      className="font-bold text-white text-base hover:text-indigo-300 transition-colors line-clamp-2"
                    >
                      {rec.title}
                    </Link>

                    {/* Genres */}
                    <div className="flex flex-wrap gap-1.5 my-3">
                      {rec.genres.map((g) => (
                        <span
                          key={g}
                          className="rounded bg-neutral-800 px-2 py-0.5 text-[11px] font-medium text-neutral-300"
                        >
                          {g}
                        </span>
                      ))}
                    </div>

                    {/* Explanation */}
                    {rec.explanation && (
                      <div className="rounded-lg bg-neutral-950/70 p-3 border border-neutral-850 text-xs text-neutral-300 leading-relaxed italic">
                        &ldquo;{rec.explanation}&rdquo;
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="pt-4 mt-4 border-t border-neutral-800/80 flex items-center justify-between text-xs">
                    <span className="font-mono text-[11px] text-neutral-500">ID #{rec.movie_id}</span>
                    <Link
                      href={`/movies/${rec.movie_id}`}
                      className="inline-flex items-center gap-1 font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
                    >
                      <span>Movie Details</span>
                      <ArrowRight className="h-3 w-3" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}

export default function RecommendationsPage() {
  return (
    <Suspense fallback={<LoadingState message="Initializing Recommendation Engine..." />}>
      <RecommendationsContent />
    </Suspense>
  );
}
