import axios from "axios";

// In production (Vercel), VITE_API_URL points at the deployed backend's
// origin directly (e.g. https://movie-room-api.onrender.com). Locally it's
// unset, so we fall back to the Vite dev server's /api proxy, which
// forwards to http://localhost:8000 with the /api prefix stripped.
const rawApiUrl = import.meta.env.VITE_API_URL as string | undefined;
export const API_BASE_URL = rawApiUrl ? rawApiUrl.replace(/\/$/, "") : "/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});
