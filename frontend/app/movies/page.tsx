"use client";

import { useEffect, useState, useCallback } from "react";
import { Film, Filter } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { MovieSummary } from "@/lib/types";
import { MovieSearch } from "@/components/movies/MovieSearch";
import { MovieGrid } from "@/components/movies/MovieGrid";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { EngineBadge } from "@/components/ui/EngineBadge";

export default function MoviesPage() {
  const [movies, setMovies] = useState<MovieSummary[]>([]);
  const [query, setQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMovies = useCallback(async (searchQuery: string) => {
    setIsLoading(true);
    setError(null);
    try {
      if (searchQuery.trim().length > 0) {
        const results = await apiClient.searchMovies(searchQuery.trim(), 48);
        setMovies(results);
      } else {
        const initial = await apiClient.getMovies(24);
        setMovies(initial);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load movies";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMovies(query);
  }, [query, fetchMovies]);

  // Extract unique genres from currently loaded movies
  const availableGenres = Array.from(
    new Set(movies.flatMap((m) => m.genres || []))
  ).sort();

  const filteredMovies = selectedGenre
    ? movies.filter((m) => m.genres?.includes(selectedGenre))
    : movies;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Film className="h-6 w-6 text-indigo-400" />
              Movie Explorer
            </h1>
            <EngineBadge engine="neo4j" />
          </div>
          <p className="text-sm text-neutral-400 mt-1">
            Search titles, filter genres, and explore node entities in the 2,500-movie (2020–2023) dataset sample.
          </p>
        </div>

        <div className="text-xs text-neutral-500 font-mono">
          Showing {filteredMovies.length} {filteredMovies.length === 1 ? "movie" : "movies"}
        </div>
      </div>

      {/* Search Bar */}
      <div className="rounded-2xl border border-neutral-800 bg-neutral-900/40 p-6 space-y-4">
        <MovieSearch
          onSearch={(q) => {
            setQuery(q);
            setSelectedGenre(null);
          }}
          isLoading={isLoading}
        />

        {/* Genre filter tags */}
        {availableGenres.length > 0 && (
          <div className="flex items-center gap-2 pt-2 overflow-x-auto pb-1 text-xs">
            <span className="text-neutral-500 flex items-center gap-1 shrink-0">
              <Filter className="h-3 w-3" />
              Filter:
            </span>
            <button
              type="button"
              onClick={() => setSelectedGenre(null)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors shrink-0 ${
                selectedGenre === null
                  ? "bg-indigo-600 text-white"
                  : "bg-neutral-800 text-neutral-400 hover:text-white"
              }`}
            >
              All Genres ({movies.length})
            </button>
            {availableGenres.map((genre) => (
              <button
                key={genre}
                type="button"
                onClick={() => setSelectedGenre(selectedGenre === genre ? null : genre)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors shrink-0 ${
                  selectedGenre === genre
                    ? "bg-indigo-600 text-white"
                    : "bg-neutral-800 text-neutral-400 hover:text-white"
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Movie Results */}
      {isLoading ? (
        <LoadingState message={query ? `Searching for "${query}" in Neo4j graph...` : "Loading movies..."} />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchMovies(query)} />
      ) : filteredMovies.length === 0 ? (
        <EmptyState
          title={query ? `No movies matching "${query}"` : "No movies found"}
          description={
            query
              ? "The 2,500-movie (2020-2023) sample may not include this title. Try searching for 'Tenet', 'Soul', 'The Gentlemen', or 'Palm Springs'."
              : "No movies could be retrieved from the database."
          }
          actionLabel="Clear Search"
          onAction={() => {
            setQuery("");
            setSelectedGenre(null);
          }}
        />
      ) : (
        <div className="space-y-4">
          <MovieGrid movies={filteredMovies} showSimilarAction={true} />
        </div>
      )}
    </div>
  );
}
