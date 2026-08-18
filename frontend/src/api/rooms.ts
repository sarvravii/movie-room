import { apiClient } from "./client";
import type { RoomMembershipResponse, RoomResponse } from "../types/room";
import type { MatchResponse } from "../types/match";
import type { SwipeResponse } from "../types/swipe";

export async function createRoom(
  creatorName: string,
  genre: string,
): Promise<RoomMembershipResponse> {
  const { data } = await apiClient.post<RoomMembershipResponse>("/rooms", {
    creator_name: creatorName,
    genre,
  });
  return data;
}

export async function joinRoom(
  roomCode: string,
  userName: string,
): Promise<RoomMembershipResponse> {
  const { data } = await apiClient.post<RoomMembershipResponse>(
    `/rooms/${roomCode}/join`,
    { room_code: roomCode, user_name: userName },
  );
  return data;
}

export async function getRoom(roomCode: string): Promise<RoomResponse> {
  const { data } = await apiClient.get<RoomResponse>(`/rooms/${roomCode}`);
  return data;
}

export async function getRoomMatches(roomCode: string): Promise<MatchResponse[]> {
  const { data } = await apiClient.get<MatchResponse[]>(
    `/rooms/${roomCode}/matches`,
  );
  return data;
}

export async function submitSwipe(
  roomCode: string,
  userId: number,
  movieId: number,
  liked: boolean,
): Promise<SwipeResponse> {
  const { data } = await apiClient.post<SwipeResponse>(
    `/rooms/${roomCode}/swipe`,
    { user_id: userId, movie_id: movieId, liked },
  );
  return data;
}
