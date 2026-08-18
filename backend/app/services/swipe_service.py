import logging

from sqlalchemy.orm import Session

from app.core.exceptions import MovieNotInRoomDeckError, RoomNotFoundError, UserNotInRoomError
from app.core.ws_events import WSEventType
from app.core.ws_manager import manager
from app.db.models import Room, Swipe
from app.repositories import (
    match_repository,
    movie_repository,
    room_movie_repository,
    room_repository,
    swipe_repository,
)
from app.schemas.swipe import SwipeResponse

logger = logging.getLogger(__name__)


def _to_swipe_response(swipe: Swipe) -> SwipeResponse:
    return SwipeResponse(
        id=swipe.id,
        room_id=swipe.room_id,
        user_id=swipe.user_id,
        movie_id=swipe.movie_id,
        liked=swipe.liked,
        created_at=swipe.created_at,
    )


async def _broadcast_swipe_events(db: Session, room: Room, swipe: Swipe) -> None:
    # Never let a WebSocket delivery problem (or a bug in this best-effort
    # logic) turn a successful swipe into a failed HTTP response.
    try:
        room_progress = swipe_repository.get_room_swipe_progress(db, room.id)
        await manager.broadcast(
            room.code,
            {
                "type": WSEventType.USER_SWIPED,
                "user_id": swipe.user_id,
                "movie_id": swipe.movie_id,
                "room_swipe_progress": room_progress,
            },
        )

        if not swipe.liked:
            return

        positive_count, _total_swipes = swipe_repository.get_swipe_counts_for_movie(
            db, room.id, swipe.movie_id
        )
        total_participants = room_repository.get_member_count(db, room.id)

        if total_participants <= 0 or positive_count != total_participants:
            return

        # Full group agreement — only broadcast the first time this happens
        # for this movie in this room (the "matches" table is our record of that).
        if match_repository.get_match(db, room.id, swipe.movie_id) is not None:
            return

        match_repository.create_match(db, room.id, swipe.movie_id)
        movies = movie_repository.get_movies_by_ids(db, [swipe.movie_id])
        if not movies:
            return

        await manager.broadcast(
            room.code,
            {
                "type": WSEventType.MOVIE_MATCHED,
                "movie_id": movies[0].id,
                "title": movies[0].title,
                "group_score": positive_count / total_participants,
            },
        )
    except Exception:
        logger.exception("Failed to broadcast swipe events for room %s", room.code)


async def record_swipe(db: Session, room_code: str, user_id: int, movie_id: int, liked: bool) -> SwipeResponse:
    room = room_repository.get_room_by_code(db, room_code)
    if room is None:
        raise RoomNotFoundError(f"No room found with code {room_code}")

    if not room_repository.is_member(db, room.id, user_id):
        raise UserNotInRoomError(f"User {user_id} is not a member of room {room.id}")

    if not room_movie_repository.is_movie_in_room_deck(db, room.id, movie_id):
        raise MovieNotInRoomDeckError(f"Movie {movie_id} is not part of room {room.id}'s deck")

    # Propagates DuplicateSwipeError if this user already swiped on this movie in this room.
    swipe = swipe_repository.create_swipe(db, room_id=room.id, user_id=user_id, movie_id=movie_id, liked=liked)
    await _broadcast_swipe_events(db, room, swipe)

    return _to_swipe_response(swipe)
