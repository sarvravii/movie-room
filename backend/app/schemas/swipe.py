from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SwipeRequest(BaseModel):
    user_id: int
    movie_id: int
    liked: bool


class SwipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    movie_id: int
    liked: bool
    created_at: datetime
