export interface MatchResponse {
  movie_id: number;
  title: string;
  poster_url: string | null;
  positive_count: number;
  total_swipes: number;
  total_participants: number;
  group_score: number;
}
