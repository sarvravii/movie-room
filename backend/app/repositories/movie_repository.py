from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Genre, Movie, MovieGenre


def _parse_release_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def upsert_movies_from_tmdb(
    db: Session,
    tmdb_movies: list[dict[str, Any]],
    genre_lookup: Optional[dict[int, str]] = None,
) -> None:
    """Insert/update movies from raw TMDB dicts and seed any missing genres.

    genre_lookup maps TMDB genre id -> genre name, needed because /discover/movie
    results only carry genre_ids, not names.
    """
    genre_lookup = genre_lookup or {}

    referenced_tmdb_genre_ids = {
        genre_id for movie in tmdb_movies for genre_id in movie.get("genre_ids", [])
    }

    genres_by_tmdb_id: dict[int, Genre] = {}
    if referenced_tmdb_genre_ids:
        existing_genres = db.execute(
            select(Genre).where(Genre.tmdb_id.in_(referenced_tmdb_genre_ids))
        ).scalars().all()
        genres_by_tmdb_id = {g.tmdb_id: g for g in existing_genres}

    for tmdb_genre_id in referenced_tmdb_genre_ids:
        if tmdb_genre_id not in genres_by_tmdb_id:
            name = genre_lookup.get(tmdb_genre_id, f"Unknown ({tmdb_genre_id})")
            genre = Genre(tmdb_id=tmdb_genre_id, name=name)
            db.add(genre)
            genres_by_tmdb_id[tmdb_genre_id] = genre
    db.flush()

    for tmdb_movie in tmdb_movies:
        tmdb_id = tmdb_movie["id"]
        movie = db.execute(select(Movie).where(Movie.tmdb_id == tmdb_id)).scalar_one_or_none()

        if movie is None:
            movie = Movie(tmdb_id=tmdb_id)
            db.add(movie)

        movie.title = tmdb_movie.get("title", "")
        movie.overview = tmdb_movie.get("overview")
        movie.poster_path = tmdb_movie.get("poster_path")
        movie.release_date = _parse_release_date(tmdb_movie.get("release_date"))
        movie.vote_average = tmdb_movie.get("vote_average")
        db.flush()

        existing_genre_ids = {
            mg.genre_id
            for mg in db.execute(
                select(MovieGenre).where(MovieGenre.movie_id == movie.id)
            ).scalars().all()
        }
        for tmdb_genre_id in tmdb_movie.get("genre_ids", []):
            genre = genres_by_tmdb_id.get(tmdb_genre_id)
            if genre is None or genre.id in existing_genre_ids:
                continue
            db.add(MovieGenre(movie_id=movie.id, genre_id=genre.id))
            existing_genre_ids.add(genre.id)

    db.commit()


def get_movies_by_genre(db: Session, genre_name: str, limit: int = 20) -> list[Movie]:
    stmt = (
        select(Movie)
        .join(MovieGenre, MovieGenre.movie_id == Movie.id)
        .join(Genre, Genre.id == MovieGenre.genre_id)
        .where(Genre.name.ilike(genre_name.strip()))
        .options(selectinload(Movie.movie_genres).selectinload(MovieGenre.genre))
        .order_by(Movie.vote_average.desc().nullslast())
        .distinct()
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def get_movies_by_ids(db: Session, movie_ids: list[int]) -> list[Movie]:
    if not movie_ids:
        return []
    return list(db.execute(select(Movie).where(Movie.id.in_(movie_ids))).scalars().all())
