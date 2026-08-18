import { useEffect, useRef } from "react";
import type { WSEvent } from "../types/ws";

export function useRoomSocket(
  roomCode: string | undefined,
  onMessage: (event: WSEvent) => void,
) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!roomCode) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/rooms/${roomCode}`);

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
