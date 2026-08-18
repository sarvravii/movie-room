class RoomNotFoundError(Exception):
    """Raised when a room code does not match any existing room."""


class AlreadyJoinedError(Exception):
    """Raised when a user attempts to join a room they are already a member of."""


class TMDBServiceError(Exception):
    """Raised when a call to the TMDB API fails (bad key, rate limit, network error)."""


class UnrecognizedGenreError(Exception):
    """Raised when a genre name doesn't match any of TMDB's known movie genres."""


class DuplicateSwipeError(Exception):
    """Raised when a user swipes on a movie they've already swiped on in this room."""


class UserNotInRoomError(Exception):
    """Raised when a user tries to act in a room they are not a member of."""


class MovieNotInRoomDeckError(Exception):
    """Raised when a user swipes on a movie that isn't part of the room's assigned deck."""
