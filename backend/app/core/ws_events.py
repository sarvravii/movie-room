from enum import StrEnum


class WSEventType(StrEnum):
    USER_JOINED = "user_joined"
    USER_SWIPED = "user_swiped"
    MOVIE_MATCHED = "movie_matched"
