import { MovieSummary } from "@/lib/types";
import { MovieCard } from "./MovieCard";

interface MovieGridProps {
  movies: MovieSummary[];
  showSimilarAction?: boolean;
}

export function MovieGrid({ movies, showSimilarAction = true }: MovieGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {movies.map((movie) => (
        <MovieCard
          key={movie.movie_id}
          movie={movie}
          showSimilarAction={showSimilarAction}
        />
      ))}
    </div>
  );
}
