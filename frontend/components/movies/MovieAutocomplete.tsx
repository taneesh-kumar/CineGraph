"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, Loader2, X, Film, Check } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { MovieSummary } from "@/lib/types";

interface MovieAutocompleteProps {
  onSelectMovie: (movie: MovieSummary) => void;
  selectedMovie?: MovieSummary | null;
  placeholder?: string;
  className?: string;
  label?: string;
}

const QUICK_SAMPLES = [
  "Tenet",
  "Soul",
  "The Gentlemen",
  "Palm Springs",
  "Dune",
];

export function MovieAutocomplete({
  onSelectMovie,
  selectedMovie,
  placeholder = "Search movie by title (e.g. Tenet, Soul, Dune)...",
  className = "",
  label,
}: MovieAutocompleteProps) {
  const [query, setQuery] = useState(selectedMovie ? selectedMovie.title : "");
  const [results, setResults] = useState<MovieSummary[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [noResultsFound, setNoResultsFound] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Sync query if selectedMovie changes externally
  useEffect(() => {
    if (selectedMovie) {
      setQuery(selectedMovie.title);
    }
  }, [selectedMovie]);

  // Click outside listener to close dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setResults([]);
      setNoResultsFound(false);
      setIsLoading(false);
      return;
    }

    // Don't search if the query exactly matches current selected movie title
    if (selectedMovie && query.trim().toLowerCase() === selectedMovie.title.toLowerCase()) {
      return;
    }

    setIsLoading(true);
    setNoResultsFound(false);

    const timer = setTimeout(async () => {
      try {
        const data = await apiClient.searchMovies(query.trim(), 8);
        setResults(data);
        setNoResultsFound(data.length === 0);
        setIsOpen(true);
      } catch (err) {
        console.error("Movie search failed:", err);
        setResults([]);
        setNoResultsFound(true);
      } finally {
        setIsLoading(false);
      }
    }, 280);

    return () => clearTimeout(timer);
  }, [query, selectedMovie]);

  const handleSelect = (movie: MovieSummary) => {
    setQuery(movie.title);
    setIsOpen(false);
    onSelectMovie(movie);
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
    setNoResultsFound(false);
    setIsOpen(false);
  };

  const handleQuickSample = async (sampleTitle: string) => {
    setQuery(sampleTitle);
    setIsLoading(true);
    try {
      const data = await apiClient.searchMovies(sampleTitle, 1);
      if (data && data.length > 0) {
        handleSelect(data[0]);
      }
    } catch (err) {
      console.error("Quick sample lookup failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (results.length > 0) {
        handleSelect(results[0]);
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  return (
    <div ref={containerRef} className={`relative w-full space-y-2 ${className}`}>
      {label && (
        <label className="text-xs font-semibold text-neutral-300 block">
          {label}
        </label>
      )}

      <div className="relative flex items-center">
        <div className="absolute left-3.5 text-neutral-500 pointer-events-none">
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin text-indigo-400" />
          ) : (
            <Search className="h-4 w-4" />
          )}
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => {
            if (results.length > 0) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full rounded-xl border border-neutral-800 bg-neutral-950 pl-10 pr-10 py-2.5 text-sm text-white placeholder:text-neutral-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-colors shadow-inner"
        />

        {query && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 p-1 rounded-md text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
            title="Clear search"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 z-50 mt-1 max-h-64 overflow-y-auto rounded-xl border border-neutral-800 bg-neutral-900/95 backdrop-blur-md shadow-2xl divide-y divide-neutral-800/60">
          {results.length > 0 ? (
            results.map((movie) => {
              const isSelected = selectedMovie?.movie_id === movie.movie_id;
              return (
                <button
                  key={movie.movie_id}
                  type="button"
                  onClick={() => handleSelect(movie)}
                  className={`w-full flex items-center justify-between gap-3 px-3.5 py-2.5 text-left text-xs transition-colors ${
                    isSelected
                      ? "bg-indigo-600/15 text-indigo-300"
                      : "text-neutral-200 hover:bg-neutral-800/80"
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Film className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
                    <div className="truncate">
                      <span className="font-semibold text-white">{movie.title}</span>
                      {(movie.year || movie.release_year) && (
                        <span className="text-neutral-400 ml-1.5 font-mono text-[11px]">
                          ({movie.year || movie.release_year})
                        </span>
                      )}
                      {movie.genres && movie.genres.length > 0 && (
                        <span className="text-neutral-500 ml-2 text-[11px] truncate">
                          • {movie.genres.slice(0, 3).join(", ")}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="shrink-0 flex items-center gap-2">
                    {isSelected && <Check className="h-3.5 w-3.5 text-indigo-400" />}
                  </div>
                </button>
              );
            })
          ) : noResultsFound ? (
            <div className="px-4 py-3 text-xs text-neutral-400 text-center">
              No movies found matching &ldquo;{query}&rdquo;
            </div>
          ) : null}
        </div>
      )}

      {/* Suggested Quick Searches */}
      <div className="flex flex-wrap items-center gap-1.5 text-xs text-neutral-400 pt-0.5">
        <span className="text-neutral-500 text-[11px]">Quick Picks:</span>
        {QUICK_SAMPLES.map((title) => (
          <button
            key={title}
            type="button"
            onClick={() => handleQuickSample(title)}
            className="rounded-md border border-neutral-800 bg-neutral-900/70 px-2 py-0.5 text-[11px] text-neutral-300 hover:border-neutral-700 hover:text-white transition-colors"
          >
            {title}
          </button>
        ))}
      </div>
    </div>
  );
}
