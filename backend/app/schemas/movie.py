from typing import List, Optional

from pydantic import BaseModel


class MovieResponse(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    release_year: Optional[int] = None
    poster_url: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = []
