export interface UserJoinedEvent {
  type: "user_joined";
  user_id: number;
  display_name: string;
  member_count: number;
}

export interface RoomSwipeProgressMember {
  user_id: number;
  swiped_count: number;
}

export interface RoomSwipeProgress {
  deck_size: number;
  members: RoomSwipeProgressMember[];
}

export interface UserSwipedEvent {
  type: "user_swiped";
  user_id: number;
  movie_id: number;
  room_swipe_progress: RoomSwipeProgress;
}

export interface MovieMatchedEvent {
  type: "movie_matched";
  movie_id: number;
  title: string;
  group_score: number;
}

export type WSEvent = UserJoinedEvent | UserSwipedEvent | MovieMatchedEvent;
