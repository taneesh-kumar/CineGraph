import Link from "next/link";
import { Star, Sparkles, ArrowRight } from "lucide-react";
import { MovieSummary } from "@/lib/types";

interface MovieCardProps {
  movie: MovieSummary;
  showSimilarAction?: boolean;
}

export function MovieCard({ movie, showSimilarAction = true }: MovieCardProps) {
  return (
    <div className="group flex flex-col justify-between rounded-xl border border-neutral-800/80 bg-neutral-900/60 p-5 shadow-sm transition-all duration-200 hover:border-neutral-700 hover:bg-neutral-900 hover:shadow-md hover:shadow-indigo-950/20">
      <div>
        {/* Top Header: ID */}
        <div className="flex items-center justify-between gap-2 text-xs text-neutral-500 mb-2">
          <span className="font-mono text-[11px] text-neutral-400">ID #{movie.movie_id}</span>
        </div>

        {/* Title & Year */}
        <div className="mb-3">
          <Link
            href={`/movies/${movie.movie_id}`}
            className="group-hover:text-indigo-300 text-white font-semibold text-base leading-snug line-clamp-2 transition-colors"
          >
            {movie.title}
          </Link>
          {(movie.year || movie.release_year) ? (
            <span className="inline-block mt-1 text-xs font-medium text-neutral-400">
              {movie.year || movie.release_year}
            </span>
          ) : (
            <span className="inline-block mt-1 text-xs text-neutral-600">Year N/A</span>
          )}
        </div>

        {/* Genres */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {movie.genres && movie.genres.length > 0 ? (
            movie.genres.map((genre) => (
              <span
                key={genre}
                className="inline-flex items-center rounded-md bg-neutral-800/90 px-2 py-0.5 text-[11px] font-medium text-neutral-300 border border-neutral-700/50"
              >
                {genre}
              </span>
            ))
          ) : (
            <span className="text-xs text-neutral-500 italic">No genres listed</span>
          )}
        </div>
      </div>

      {/* Ratings and Actions */}
      <div className="pt-3 border-t border-neutral-800/70 space-y-3">
        {(movie.avg_rating ?? movie.average_rating) !== undefined &&
        (movie.avg_rating ?? movie.average_rating) !== null ? (
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-1.5 text-amber-400 font-semibold">
              <Star className="h-3.5 w-3.5 fill-amber-400" />
              <span>{(movie.avg_rating ?? movie.average_rating)!.toFixed(2)}</span>
            </div>
            <span className="text-neutral-500 font-mono text-[11px]">
              {movie.rating_count ? `${movie.rating_count.toLocaleString()} ratings` : "No ratings"}
            </span>
          </div>
        ) : null}

        <div className="flex items-center justify-between gap-2 text-xs pt-1">
          <Link
            href={`/movies/${movie.movie_id}`}
            className="inline-flex items-center gap-1 text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
          >
            <span>Details</span>
            <ArrowRight className="h-3 w-3" />
          </Link>

          {showSimilarAction && (
            <Link
              href={`/recommendations?movie_id=${movie.movie_id}`}
              className="inline-flex items-center gap-1 rounded bg-neutral-800 hover:bg-neutral-700 px-2 py-1 text-[11px] text-neutral-300 transition-colors"
              title="Find similar movies"
            >
              <Sparkles className="h-3 w-3 text-indigo-400" />
              <span>Similar</span>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
