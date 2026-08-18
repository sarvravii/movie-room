from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Movie, MovieGenre, RoomMovie


def is_room_populated(db: Session, room_id: int) -> bool:
    return (
        db.execute(select(RoomMovie.id).where(RoomMovie.room_id == room_id).limit(1)).scalar_one_or_none()
        is not None
    )


def populate_room_movies(db: Session, room_id: int, movie_ids: list[int]) -> None:
    # Idempotent: if a deck already exists for this room, leave it untouched
    # so re-fetching never duplicates rows or reshuffles order.
    if is_room_populated(db, room_id):
        return

    for order, movie_id in enumerate(movie_ids):
        db.add(RoomMovie(room_id=room_id, movie_id=movie_id, display_order=order))
    db.commit()


def get_room_movies(db: Session, room_id: int) -> list[Movie]:
    stmt = (
        select(Movie)
        .join(RoomMovie, RoomMovie.movie_id == Movie.id)
        .where(RoomMovie.room_id == room_id)
        .options(selectinload(Movie.movie_genres).selectinload(MovieGenre.genre))
        .order_by(RoomMovie.display_order)
    )
    return list(db.execute(stmt).scalars().all())


def is_movie_in_room_deck(db: Session, room_id: int, movie_id: int) -> bool:
    return (
        db.execute(
            select(RoomMovie.id).where(RoomMovie.room_id == room_id, RoomMovie.movie_id == movie_id)
        ).scalar_one_or_none()
        is not None
    )
