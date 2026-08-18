import json
from typing import Any, Optional

import redis

from app.config import settings

_redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

_CACHE_KEY_PREFIX = "movies:tmdb:"


def _cache_key(genre_name: str) -> str:
    # Normalized (lowercased) so "Horror" and "horror" share one cache entry.
    return f"{_CACHE_KEY_PREFIX}{genre_name.strip().lower()}"


def get_cached_movies(genre_name: str) -> Optional[list[dict[str, Any]]]:
    raw = _redis_client.get(_cache_key(genre_name))
    if raw is None:
        return None
    return json.loads(raw)


def set_cached_movies(genre_name: str, data: list[dict[str, Any]], ttl_seconds: int = 21600) -> None:
    _redis_client.set(_cache_key(genre_name), json.dumps(data), ex=ttl_seconds)
