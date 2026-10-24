import Link from "next/link";
import { Star, Sparkles, ArrowRight, Calendar } from "lucide-react";
import { MovieSummary } from "@/lib/types";

interface MovieCardProps {
  movie: MovieSummary;
  showSimilarAction?: boolean;
}

export function MovieCard({ movie, showSimilarAction = true }: MovieCardProps) {
  const rating = movie.avg_rating ?? movie.average_rating;

  return (
    <div className="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-neutral-800/80 bg-gradient-to-b from-neutral-900/80 to-neutral-950/80 p-5 shadow-sm backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:border-neutral-700 hover:shadow-xl hover:shadow-black/40">
      {/* Top subtle highlight line on hover */}
      <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-indigo-500/60 via-purple-500/60 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

      <div>
        {/* Top Header: ID & Year */}
        <div className="flex items-center justify-between gap-2 text-xs text-neutral-500 mb-2.5">
          <span className="font-mono text-[11px] text-neutral-400 bg-neutral-900 px-2 py-0.5 rounded border border-neutral-800">
            ID #{movie.movie_id}
          </span>
          {(movie.year || movie.release_year) ? (
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-neutral-400 font-mono">
              <Calendar className="h-3 w-3 text-neutral-500" />
              {movie.year || movie.release_year}
            </span>
          ) : (
            <span className="text-[11px] text-neutral-600">Year N/A</span>
          )}
        </div>

        {/* Title */}
        <div className="mb-3">
          <Link
            href={`/movies/${movie.movie_id}`}
            className="group-hover:text-indigo-300 text-white font-bold text-base leading-snug line-clamp-2 transition-colors block"
          >
            {movie.title}
          </Link>
        </div>

        {/* Genres */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {movie.genres && movie.genres.length > 0 ? (
            movie.genres.slice(0, 4).map((genre) => (
              <span
                key={genre}
                className="inline-flex items-center rounded-lg bg-neutral-900/90 px-2.5 py-0.5 text-[11px] font-medium text-neutral-300 border border-neutral-800"
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
      <div className="pt-3 border-t border-neutral-800/80 space-y-3">
        {rating !== undefined && rating !== null ? (
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-1.5 font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded-lg border border-amber-400/20">
              <Star className="h-3.5 w-3.5 fill-amber-400" />
              <span>{rating.toFixed(2)}</span>
            </div>
            <span className="text-neutral-500 font-mono text-[11px]">
              {movie.rating_count ? `${movie.rating_count.toLocaleString()} ratings` : "No ratings"}
            </span>
          </div>
        ) : null}

        <div className="flex items-center justify-between gap-2 text-xs pt-1">
          <Link
            href={`/movies/${movie.movie_id}`}
            className="inline-flex items-center gap-1 text-indigo-400 hover:text-indigo-300 font-semibold transition-colors"
          >
            <span>Details</span>
            <ArrowRight className="h-3 w-3" />
          </Link>

          {showSimilarAction && (
            <Link
              href={`/recommendations?movie_id=${movie.movie_id}`}
              className="inline-flex items-center gap-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 hover:border-neutral-700 px-2.5 py-1 text-[11px] font-medium text-neutral-300 hover:text-white transition-all shadow-sm"
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
