from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateRoomRequest(BaseModel):
    creator_name: str
    genre: str


class JoinRoomRequest(BaseModel):
    room_code: str
    user_name: str


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    genre: str
    status: str
    created_at: datetime
    member_count: int


class RoomMembershipResponse(RoomResponse):
    """RoomResponse plus the calling user's own id — for endpoints where a
    specific user is doing the calling (create/join), unlike the plain
    room lookup which has no single "calling user"."""

    user_id: int
