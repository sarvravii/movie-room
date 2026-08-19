import { useEffect, useRef } from "react";
import type { WSEvent } from "../types/ws";

function getWebSocketUrl(roomCode: string): string {
  const rawApiUrl = import.meta.env.VITE_API_URL as string | undefined;

  if (rawApiUrl) {
    // Production: derive the WebSocket origin from the same deployed
    // backend URL used for HTTP requests (http -> ws, https -> wss).
    const wsOrigin = rawApiUrl.replace(/\/$/, "").replace(/^http/, "ws");
    return `${wsOrigin}/ws/rooms/${roomCode}`;
  }

  // Local dev: relies on the Vite dev server's /ws proxy to localhost:8000.
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws/rooms/${roomCode}`;
}

export function useRoomSocket(
  roomCode: string | undefined,
  onMessage: (event: WSEvent) => void,
) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!roomCode) return;

    const ws = new WebSocket(getWebSocketUrl(roomCode));

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WSEvent;
        onMessageRef.current(data);
      } catch {
        // ignore malformed messages
      }
    };

    return () => {
      ws.close();
    };
  }, [roomCode]);
}
