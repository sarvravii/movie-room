export interface SwipeRequest {
  user_id: number;
  movie_id: number;
  liked: boolean;
}

export interface SwipeResponse {
  id: number;
  room_id: number;
  user_id: number;
  movie_id: number;
  liked: boolean;
  created_at: string;
}
