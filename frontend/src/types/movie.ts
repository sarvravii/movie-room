export interface MovieResponse {
  id: number;
  title: string;
  overview: string | null;
  release_year: number | null;
  poster_url: string | null;
  rating: number | null;
  genres: string[];
}
