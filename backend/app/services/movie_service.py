from sqlalchemy.orm import Session

from app.db.models import Movie
from app.repositories import movie_repository
from app.schemas.movie import MovieResponse
from app.services import cache_service, tmdb_client

TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def to_movie_response(movie: Movie) -> MovieResponse:
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        overview=movie.overview,
        release_year=movie.release_date.year if movie.release_date else None,
        poster_url=f"{TMDB_IMAGE_BASE_URL}{movie.poster_path}" if movie.poster_path else None,
        rating=movie.vote_average,
        genres=[mg.genre.name for mg in movie.movie_genres],
    )


async def get_or_fetch_movies_by_genre(db: Session, genre_name: str, limit: int = 20) -> list[MovieResponse]:
    cached = cache_service.get_cached_movies(genre_name)

    if cached is None:
        # Raises UnrecognizedGenreError / TMDBServiceError, which the router translates to HTTP errors.
        tmdb_movies = await tmdb_client.discover_movies_by_genre(genre_name)
        cache_service.set_cached_movies(genre_name, tmdb_movies)

        tmdb_genres = await tmdb_client.get_genres()
        genre_lookup = {g["id"]: g["name"] for g in tmdb_genres}
        movie_repository.upsert_movies_from_tmdb(db, tmdb_movies, genre_lookup=genre_lookup)

    movies = movie_repository.get_movies_by_genre(db, genre_name, limit=limit)
    return [to_movie_response(m) for m in movies]
