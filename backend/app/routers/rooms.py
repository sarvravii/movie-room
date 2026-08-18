from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AlreadyJoinedError,
    DuplicateSwipeError,
    MovieNotInRoomDeckError,
    RoomNotFoundError,
    TMDBServiceError,
    UnrecognizedGenreError,
    UserNotInRoomError,
)
from app.db.session import get_db
from app.schemas.match import MatchResponse
from app.schemas.movie import MovieResponse
from app.schemas.room import CreateRoomRequest, JoinRoomRequest, RoomMembershipResponse, RoomResponse
from app.schemas.swipe import SwipeRequest, SwipeResponse
from app.services import match_service, room_movie_service, room_service, swipe_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=RoomMembershipResponse, status_code=status.HTTP_201_CREATED)
def create_room(payload: CreateRoomRequest, db: Session = Depends(get_db)) -> RoomMembershipResponse:
    return room_service.create_room(db, creator_name=payload.creator_name, genre=payload.genre)


@router.post("/{room_code}/join", response_model=RoomMembershipResponse)
async def join_room(
    room_code: str, payload: JoinRoomRequest, db: Session = Depends(get_db)
) -> RoomMembershipResponse:
    try:
        return await room_service.join_room(db, room_code=room_code, user_name=payload.user_name)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AlreadyJoinedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{room_code}", response_model=RoomResponse)
def get_room(room_code: str, db: Session = Depends(get_db)) -> RoomResponse:
    try:
        return room_service.get_room(db, room_code=room_code)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{room_code}/movies", response_model=List[MovieResponse])
async def get_room_movies(
    room_code: str,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[MovieResponse]:
    try:
        room = room_service.get_room(db, room_code=room_code)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    try:
        return await room_movie_service.get_or_build_room_deck(db, room_id=room.id, limit=limit)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UnrecognizedGenreError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except TMDBServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/{room_code}/swipe", response_model=SwipeResponse, status_code=status.HTTP_201_CREATED)
async def swipe(room_code: str, payload: SwipeRequest, db: Session = Depends(get_db)) -> SwipeResponse:
    try:
        return await swipe_service.record_swipe(
            db,
            room_code=room_code,
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            liked=payload.liked,
        )
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserNotInRoomError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except MovieNotInRoomDeckError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicateSwipeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{room_code}/matches", response_model=List[MatchResponse])
def get_room_matches(room_code: str, db: Session = Depends(get_db)) -> List[MatchResponse]:
    try:
        return match_service.get_room_matches(db, room_code=room_code)
    except RoomNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
