from typing import Optional

from pydantic import BaseModel


class MatchResponse(BaseModel):
    movie_id: int
    title: str
    poster_url: Optional[str] = None
    positive_count: int
    total_swipes: int
    total_participants: int
    group_score: float
