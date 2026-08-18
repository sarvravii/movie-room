import logging

from sqlalchemy.orm import Session

from app.core.exceptions import RoomNotFoundError
from app.core.ws_events import WSEventType
from app.core.ws_manager import manager
from app.db.models import Room, User
from app.repositories import room_repository, user_repository
from app.schemas.room import RoomMembershipResponse, RoomResponse

logger = logging.getLogger(__name__)


def _to_response(room: Room, member_count: int) -> RoomResponse:
    return RoomResponse(
        id=room.id,
        code=room.code,
        genre=room.genre,
        status=room.status,
        created_at=room.created_at,
        member_count=member_count,
    )


def _to_membership_response(room: Room, member_count: int, user_id: int) -> RoomMembershipResponse:
    return RoomMembershipResponse(
        id=room.id,
        code=room.code,
        genre=room.genre,
        status=room.status,
        created_at=room.created_at,
        member_count=member_count,
        user_id=user_id,
    )


def create_room(db: Session, creator_name: str, genre: str) -> RoomMembershipResponse:
    creator = user_repository.get_or_create_guest_user(db, creator_name)
    room = room_repository.create_room(db, genre=genre, creator_id=creator.id)
    member_count = room_repository.get_member_count(db, room.id)
    return _to_membership_response(room, member_count, user_id=creator.id)


async def _broadcast_user_joined(room_code: str, user: User, member_count: int) -> None:
    # Never let a WebSocket delivery problem turn a successful join into a failed HTTP response.
    try:
        await manager.broadcast(
            room_code,
            {
                "type": WSEventType.USER_JOINED,
                "user_id": user.id,
                "display_name": user.display_name,
                "member_count": member_count,
            },
        )
    except Exception:
        logger.exception("Failed to broadcast user_joined for room %s", room_code)


async def join_room(db: Session, room_code: str, user_name: str) -> RoomMembershipResponse:
    room = room_repository.get_room_by_code(db, room_code)
    if room is None:
        raise RoomNotFoundError(f"No room found with code {room_code}")

    user = user_repository.get_or_create_guest_user(db, user_name)
    # Propagates AlreadyJoinedError if this user is already a member.
    room_repository.add_member(db, room_id=room.id, user_id=user.id)

    member_count = room_repository.get_member_count(db, room.id)
    await _broadcast_user_joined(room.code, user, member_count)

    return _to_membership_response(room, member_count, user_id=user.id)


def get_room(db: Session, room_code: str) -> RoomResponse:
    room = room_repository.get_room_by_code(db, room_code)
    if room is None:
        raise RoomNotFoundError(f"No room found with code {room_code}")

    member_count = room_repository.get_member_count(db, room.id)
    return _to_response(room, member_count)
