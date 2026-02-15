from fastapi import APIRouter, HTTPException, Request

from spotifeel_api.config import get_settings
from spotifeel_api.spotify_client import spotify_get
from spotifeel_api.token_store import load_token

router = APIRouter(prefix="/user", tags=["user-data"])

USER_COOKIE = "spotifeel_uid"


def _require_user_id(request: Request) -> str:
    uid = request.cookies.get(USER_COOKIE)
    if not uid:
        raise HTTPException(status_code=401, detail="Not logged in. Go to /auth/login")
    return uid


def _require_access_token(settings, uid: str) -> str:
    token = load_token(settings.token_dir, uid)
    if not token or "access_token" not in token:
        raise HTTPException(status_code=401, detail="Token missing for this user. Login again.")
    return token["access_token"]


@router.get("/me")
async def me(request: Request):
    settings = get_settings()
    uid = _require_user_id(request)
    access_token = _require_access_token(settings, uid)
    return await spotify_get(access_token, "/me")


@router.get("/top-tracks")
async def top_tracks(request: Request, limit: int = 20, time_range: str = "medium_term"):
    settings = get_settings()
    uid = _require_user_id(request)
    access_token = _require_access_token(settings, uid)

    return await spotify_get(
        access_token,
        "/me/top/tracks",
        {"limit": limit, "time_range": time_range},
    )


@router.get("/top-artists")
async def top_artists(request: Request, limit: int = 20, time_range: str = "medium_term"):
    settings = get_settings()
    uid = _require_user_id(request)
    access_token = _require_access_token(settings, uid)

    return await spotify_get(
        access_token,
        "/me/top/artists",
        {"limit": limit, "time_range": time_range},
    )


@router.get("/recently-played")
async def recently_played(request: Request, limit: int = 20):
    settings = get_settings()
    uid = _require_user_id(request)
    access_token = _require_access_token(settings, uid)

    return await spotify_get(
        access_token,
        "/me/player/recently-played",
        {"limit": limit},
    )