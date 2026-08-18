import asyncio
import time
from typing import Any, Optional

import httpx

from app.config import settings
from app.core.exceptions import TMDBServiceError, UnrecognizedGenreError

_BASE_URL = "https://api.themoviedb.org/3"
_TIMEOUT = 20.0
_GENRE_CACHE_TTL_SECONDS = 3600
_MAX_ATTEMPTS = 5
_RETRY_BACKOFF_SECONDS = 0.3

# In-process cache for TMDB's genre list — it changes rarely, so we avoid
# hitting TMDB on every request just to resolve a genre name to an id.
_genre_cache: list[dict[str, Any]] = []
_genre_cache_fetched_at: float = 0.0


async def _get(path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    request_params = {"api_key": settings.TMDB_API_KEY, **(params or {})}
    # local_address="0.0.0.0" forces IPv4: this environment's IPv6 route to
    # TMDB is flaky and intermittently fails the TLS handshake.
    transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")

    last_error: Optional[httpx.TransportError] = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            async with httpx.AsyncClient(base_url=_BASE_URL, timeout=_TIMEOUT, transport=transport) as client:
                response = await client.get(path, params=request_params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise TMDBServiceError(
                f"TMDB request to {path} failed with status {exc.response.status_code}"
            ) from exc
        except httpx.TransportError as exc:
            # Transient network/connection failures are retried; other HTTPErrors are not.
            last_error = exc
            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(_RETRY_BACKOFF_SECONDS * attempt)
                continue
        except httpx.HTTPError as exc:
            reason = str(exc) or type(exc).__name__
            raise TMDBServiceError(f"TMDB request to {path} failed: {reason}") from exc

    reason = str(last_error) or type(last_error).__name__
    raise TMDBServiceError(
        f"TMDB request to {path} failed after {_MAX_ATTEMPTS} attempts: {reason}"
    ) from last_error


async def get_genres() -> list[dict[str, Any]]:
    """Fetch TMDB's genre list (id + name), used to map our genre strings to TMDB's genre IDs."""
    global _genre_cache, _genre_cache_fetched_at

    now = time.monotonic()
    if not _genre_cache or (now - _genre_cache_fetched_at) > _GENRE_CACHE_TTL_SECONDS:
        data = await _get("/genre/movie/list")
        _genre_cache = data.get("genres", [])
        _genre_cache_fetched_at = now

    return _genre_cache


async def discover_movies_by_genre(genre_name: str, page: int = 1) -> list[dict[str, Any]]:
    genres = await get_genres()
    genre_id = next(
        (g["id"] for g in genres if g["name"].lower() == genre_name.strip().lower()),
        None,
    )
    if genre_id is None:
        raise UnrecognizedGenreError(f"'{genre_name}' is not a recognized movie genre")

    data = await _get(
        "/discover/movie",
        params={"with_genres": genre_id, "sort_by": "popularity.desc", "page": page},
    )
    return data.get("results", [])
