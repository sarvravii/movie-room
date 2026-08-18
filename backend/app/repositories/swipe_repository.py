from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateSwipeError
from app.db.models import RoomMember, RoomMovie, Swipe


def create_swipe(db: Session, room_id: int, user_id: int, movie_id: int, liked: bool) -> Swipe:
    swipe = Swipe(room_id=room_id, user_id=user_id, movie_id=movie_id, liked=liked)
    db.add(swipe)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSwipeError(
            f"User {user_id} has already swiped on movie {movie_id} in room {room_id}"
        ) from exc
    db.refresh(swipe)
    return swipe


def get_swipe_counts_for_movie(db: Session, room_id: int, movie_id: int) -> tuple[int, int]:
    total = db.execute(
        select(func.count()).select_from(Swipe).where(Swipe.room_id == room_id, Swipe.movie_id == movie_id)
    ).scalar_one()
    positive = db.execute(
        select(func.count())
        .select_from(Swipe)
        .where(Swipe.room_id == room_id, Swipe.movie_id == movie_id, Swipe.liked.is_(True))
    ).scalar_one()
    return positive, total


def get_room_swipe_progress(db: Session, room_id: int) -> dict[str, Any]:
    """Per-member swipe counts vs. total deck size, e.g. for '3 of 5 people finished swiping'."""
    deck_size = db.execute(
        select(func.count()).select_from(RoomMovie).where(RoomMovie.room_id == room_id)
    ).scalar_one()

    rows = db.execute(
        select(RoomMember.user_id, func.count(Swipe.id))
        .select_from(RoomMember)
        .outerjoin(
            Swipe,
            (Swipe.room_id == RoomMember.room_id) & (Swipe.user_id == RoomMember.user_id),
        )
        .where(RoomMember.room_id == room_id)
        .group_by(RoomMember.user_id)
    ).all()

    return {
        "deck_size": deck_size,
        "members": [{"user_id": user_id, "swiped_count": count} for user_id, count in rows],
    }


def get_all_swipes_for_room(db: Session, room_id: int) -> list[Swipe]:
    return list(db.execute(select(Swipe).where(Swipe.room_id == room_id)).scalars().all())


def user_has_swiped(db: Session, room_id: int, user_id: int, movie_id: int) -> bool:
    return (
        db.execute(
            select(Swipe.id).where(
                Swipe.room_id == room_id, Swipe.user_id == user_id, Swipe.movie_id == movie_id
            )
        ).scalar_one_or_none()
        is not None
    )
