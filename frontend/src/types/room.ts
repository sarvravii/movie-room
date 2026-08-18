export interface RoomResponse {
  id: number;
  code: string;
  genre: string;
  status: string;
  created_at: string;
  member_count: number;
}

export interface RoomMembershipResponse extends RoomResponse {
  user_id: number;
}

export interface CreateRoomRequest {
  creator_name: string;
  genre: string;
}

export interface JoinRoomRequest {
  room_code: string;
  user_name: string;
}
