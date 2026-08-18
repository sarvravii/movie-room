from sqlalchemy.orm import Session

from app.core.exceptions import RoomNotFoundError
from app.repositories import room_movie_repository, room_repository
from app.schemas.movie import MovieResponse
from app.services import movie_service


async def get_or_build_room_deck(db: Session, room_id: int, limit: int = 20) -> list[MovieResponse]:
    room = room_repository.get_room_by_id(db, room_id)
    if room is None:
        raise RoomNotFoundError(f"No room found with id {room_id}")

    if not room_movie_repository.is_room_populated(db, room_id):
        # Raises UnrecognizedGenreError / TMDBServiceError, which the router translates to HTTP errors.
        movies = await movie_service.get_or_fetch_movies_by_genre(db, genre_name=room.genre, limit=limit)
        movie_ids = [m.id for m in movies]
        room_movie_repository.populate_room_movies(db, room_id, movie_ids)

    deck = room_movie_repository.get_room_movies(db, room_id)
    return [movie_service.to_movie_response(m) for m in deck]
