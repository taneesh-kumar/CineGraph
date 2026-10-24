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

  const handleSearchChange = useCallback((newQuery: string) => {
    setQuery((prev) => {
      if (prev !== newQuery) {
        setSelectedGenre(null); // only reset genre if user actually changed search text
        return newQuery;
      }
      return prev;
    });
  }, []);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-neutral-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Film className="h-6 w-6 text-indigo-400" />
            Movie Explorer
          </h1>
          <p className="text-sm text-neutral-400 mt-1">
            Search titles and filter movies by genre.
          </p>
        </div>

        <div className="text-xs text-neutral-500 font-mono">
          Showing {filteredMovies.length} {filteredMovies.length === 1 ? "movie" : "movies"}
        </div>
      </div>

      {/* Search Bar */}
      <div className="rounded-3xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/80 to-neutral-950/90 p-6 md:p-8 space-y-5 backdrop-blur-md shadow-xl shadow-black/40">
        <MovieSearch
          onSearch={handleSearchChange}
          isLoading={isLoading}
        />

        {/* Genre filter tags */}
        {availableGenres.length > 0 && (
          <div className="flex items-center gap-2 pt-1 overflow-x-auto pb-1 text-xs no-scrollbar">
            <span className="text-neutral-400 flex items-center gap-1.5 shrink-0 font-medium">
              <Filter className="h-3.5 w-3.5 text-indigo-400" />
              Filter by Genre:
            </span>
            <button
              type="button"
              onClick={() => setSelectedGenre(null)}
              className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-all shrink-0 ${
                selectedGenre === null
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 font-semibold ring-1 ring-indigo-400/50"
                  : "bg-neutral-800/70 border border-neutral-700/60 text-neutral-400 hover:text-white hover:bg-neutral-800 hover:border-neutral-600"
              }`}
            >
              All Genres ({movies.length})
            </button>
            {availableGenres.map((genre) => (
              <button
                key={genre}
                type="button"
                onClick={() => setSelectedGenre(selectedGenre === genre ? null : genre)}
                className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-all shrink-0 ${
                  selectedGenre === genre
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30 font-semibold ring-1 ring-indigo-400/50"
                    : "bg-neutral-800/70 border border-neutral-700/60 text-neutral-400 hover:text-white hover:bg-neutral-800 hover:border-neutral-600"
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
        <LoadingState message={query ? `Searching for "${query}"...` : "Loading movies..."} />
      ) : error ? (
        <ErrorState message={error} onRetry={() => fetchMovies(query)} />
      ) : filteredMovies.length === 0 ? (
        <EmptyState
          title={query ? `No movies matching "${query}"` : "No movies found"}
          description={
            query
              ? "Try searching for another movie title like 'Tenet', 'Soul', 'The Gentlemen', or 'Palm Springs'."
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
