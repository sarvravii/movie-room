from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Match


def get_match(db: Session, room_id: int, movie_id: int) -> Optional[Match]:
    return db.execute(
        select(Match).where(Match.room_id == room_id, Match.movie_id == movie_id)
    ).scalar_one_or_none()


def create_match(db: Session, room_id: int, movie_id: int) -> Match:
    match = Match(room_id=room_id, movie_id=movie_id)
    db.add(match)
    db.commit()
    db.refresh(match)
    return match
