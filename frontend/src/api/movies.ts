import { apiClient } from "./client";
import type { MovieResponse } from "../types/movie";

export async function getRoomMovies(
  roomCode: string,
  limit = 20,
): Promise<MovieResponse[]> {
  const { data } = await apiClient.get<MovieResponse[]>(
    `/rooms/${roomCode}/movies`,
    { params: { limit } },
  );
  return data;
}
