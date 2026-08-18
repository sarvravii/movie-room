from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.ws_manager import manager
from app.db.session import get_db
from app.repositories import room_repository

router = APIRouter()

# Application-specific close code (4000-4999 range is reserved for app use).
ROOM_NOT_FOUND_CLOSE_CODE = 4404


@router.websocket("/ws/rooms/{room_code}")
async def room_ws(websocket: WebSocket, room_code: str, db: Session = Depends(get_db)) -> None:
    room = room_repository.get_room_by_code(db, room_code)
    if room is None:
        await websocket.accept()
        await websocket.close(code=ROOM_NOT_FOUND_CLOSE_CODE, reason="room not found")
        return

    await manager.connect(room_code, websocket)
    try:
        while True:
            # Server -> client push only for now; just wait for the client to disconnect.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(room_code, websocket)
