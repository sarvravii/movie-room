from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import TMDBServiceError, UnrecognizedGenreError
from app.db.session import get_db
from app.schemas.movie import MovieResponse
from app.services import movie_service

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=List[MovieResponse])
async def list_movies(
    genre: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[MovieResponse]:
    if not genre or not genre.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="genre query parameter is required"
        )

    try:
        return await movie_service.get_or_fetch_movies_by_genre(db, genre_name=genre, limit=limit)
    except UnrecognizedGenreError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TMDBServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
