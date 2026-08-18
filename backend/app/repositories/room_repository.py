import secrets
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AlreadyJoinedError
from app.db.models import Room, RoomMember

# Excludes ambiguous characters 0/O and 1/I so codes are easy to read aloud.
_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_CODE_LENGTH = 6
_MAX_CODE_ATTEMPTS = 10


def _generate_room_code() -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(_CODE_LENGTH))


def create_room(db: Session, genre: str, creator_id: int) -> Room:
    last_error: Optional[IntegrityError] = None

    for _ in range(_MAX_CODE_ATTEMPTS):
        code = _generate_room_code()
        room = Room(code=code, name=f"{genre} Room", genre=genre, host_id=creator_id)
        db.add(room)
        try:
            db.flush()
        except IntegrityError as exc:
            db.rollback()
            last_error = exc
            continue

        db.add(RoomMember(room_id=room.id, user_id=creator_id))
        db.commit()
        db.refresh(room)
        return room

    raise RuntimeError("Could not generate a unique room code") from last_error


def get_room_by_code(db: Session, code: str) -> Optional[Room]:
    return db.execute(select(Room).where(Room.code == code)).scalar_one_or_none()


def get_room_by_id(db: Session, room_id: int) -> Optional[Room]:
    return db.execute(select(Room).where(Room.id == room_id)).scalar_one_or_none()


def add_member(db: Session, room_id: int, user_id: int) -> RoomMember:
    member = RoomMember(room_id=room_id, user_id=user_id)
    db.add(member)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AlreadyJoinedError(f"User {user_id} has already joined room {room_id}") from exc
    db.refresh(member)
    return member


def get_member_count(db: Session, room_id: int) -> int:
    return db.execute(
        select(func.count()).select_from(RoomMember).where(RoomMember.room_id == room_id)
    ).scalar_one()


def is_member(db: Session, room_id: int, user_id: int) -> bool:
    return (
        db.execute(
            select(RoomMember.id).where(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        ).scalar_one_or_none()
        is not None
    )
