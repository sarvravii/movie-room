import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, room_code: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(room_code, []).append(websocket)

    def disconnect(self, room_code: str, websocket: WebSocket) -> None:
        connections = self._connections.get(room_code)
        if not connections:
            return
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self._connections.pop(room_code, None)

    async def broadcast(self, room_code: str, message: dict[str, Any]) -> None:
        connections = self._connections.get(room_code)
        if not connections:
            return

        dead: list[WebSocket] = []
        for connection in list(connections):
            try:
                await connection.send_json(message)
            except Exception:
                logger.info("Dropping dead WebSocket connection in room %s", room_code)
                dead.append(connection)

        for connection in dead:
            self.disconnect(room_code, connection)


manager = ConnectionManager()
