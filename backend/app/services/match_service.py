from collections import defaultdict

from sqlalchemy.orm import Session

from app.core.exceptions import RoomNotFoundError
from app.db.models import Swipe
from app.repositories import movie_repository, room_repository, swipe_repository
from app.schemas.match import MatchResponse
from app.services.movie_service import TMDB_IMAGE_BASE_URL
from app.services.scorers import rule_based_scorer


def get_room_matches(db: Session, room_code: str, min_swipe_coverage: float = 0.0) -> list[MatchResponse]:
    room = room_repository.get_room_by_code(db, room_code)
    if room is None:
        raise RoomNotFoundError(f"No room found with code {room_code}")

    # Accepted but not yet enforced: requiring full swipe coverage doesn't make
    # sense while group swiping is still in progress for most of a room's
    # life. This will matter once a "room complete" state exists to signal
    # everyone is actually done.
    del min_swipe_coverage

    total_participants = room_repository.get_member_count(db, room.id)

    swipes = swipe_repository.get_all_swipes_for_room(db, room.id)
    swipes_by_movie: dict[int, list[Swipe]] = defaultdict(list)
    for swipe in swipes:
        swipes_by_movie[swipe.movie_id].append(swipe)

    if not swipes_by_movie:
        return []

    movies_by_id = {m.id: m for m in movie_repository.get_movies_by_ids(db, list(swipes_by_movie.keys()))}

    scored: list[MatchResponse] = []
    for movie_id, movie_swipes in swipes_by_movie.items():
        movie = movies_by_id.get(movie_id)
        if movie is None:
            continue  # defensive: swipes should always reference a real movie

        positive_count = sum(1 for s in movie_swipes if s.liked)
        total_swipes = len(movie_swipes)
        group_score = rule_based_scorer.score_movie(
            positive_swipes=positive_count,
            total_swipes=total_swipes,
            total_participants=total_participants,
        )

        scored.append(
            MatchResponse(
                movie_id=movie.id,
                title=movie.title,
                poster_url=f"{TMDB_IMAGE_BASE_URL}{movie.poster_path}" if movie.poster_path else None,
                positive_count=positive_count,
                total_swipes=total_swipes,
                total_participants=total_participants,
                group_score=group_score,
            )
        )

    scored.sort(key=lambda m: (-m.group_score, -m.positive_count, m.movie_id))
    return scored
