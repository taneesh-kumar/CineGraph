"use client";

import { useState, useEffect } from "react";
import { Search, X, Loader2 } from "lucide-react";

interface MovieSearchProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
  initialQuery?: string;
  placeholder?: string;
}

const SAMPLE_QUERIES = ["Tenet", "Soul", "The Gentlemen", "Palm Springs", "Dune"];

export function MovieSearch({
  onSearch,
  isLoading = false,
  initialQuery = "",
  placeholder = "Search movies by title (e.g. Tenet, Soul, Palm Springs)...",
}: MovieSearchProps) {
  const [value, setValue] = useState(initialQuery);

  useEffect(() => {
    const handler = setTimeout(() => {
      onSearch(value.trim());
    }, 350);

    return () => clearTimeout(handler);
  }, [value, onSearch]);

  const handleClear = () => {
    setValue("");
    onSearch("");
  };

  return (
    <div className="w-full space-y-3">
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
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          className="w-full rounded-xl border border-neutral-800 bg-neutral-900/90 pl-10 pr-10 py-3 text-sm text-neutral-100 placeholder:text-neutral-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-colors shadow-inner"
          aria-label="Search movies by title"
        />
        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 p-1 rounded-md text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
            aria-label="Clear search query"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Suggested chips */}
      <div className="flex flex-wrap items-center gap-1.5 text-xs text-neutral-400">
        <span className="text-neutral-500">Sample searches:</span>
        {SAMPLE_QUERIES.map((sample) => (
          <button
            key={sample}
            type="button"
            onClick={() => setValue(sample)}
            className="rounded-md border border-neutral-800 bg-neutral-900/60 px-2 py-0.5 text-neutral-300 hover:border-neutral-700 hover:text-white transition-colors"
          >
            {sample}
          </button>
        ))}
      </div>
    </div>
  );
}
