from typing import Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from spotifeel_api.config import get_settings
from spotifeel_api.spotify_oauth import build_login_url, exchange_code_for_token, new_state, refresh_access_token
from spotifeel_api.spotify_client import spotify_get
from spotifeel_api.token_store import load_token, save_token, delete_token
from spotifeel_api.routes.user_data import router as user_data_router

TimeRange = Literal["short_term", "medium_term", "long_term"]
app = FastAPI(title="spotifeel api")
app.include_router(user_data_router)

STATE_COOKIE = "spotify_auth_state"
USER_COOKIE = "spotifeel_uid"

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/auth/login")
def auth_login():
    settings = get_settings()
    state = new_state()
    url = build_login_url(settings.spotify_client_id, settings.spotify_redirect_uri, state)

    resp = RedirectResponse(url)
    resp.set_cookie(STATE_COOKIE, state, httponly=True, samesite="lax", max_age=300)
    return resp

@app.get("/auth/callback")
async def auth_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail=f"Spotify auth error: {error}")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code/state")

    stored_state = request.cookies.get(STATE_COOKIE)
    if stored_state is None or stored_state != state:
        raise HTTPException(status_code=400, detail="state_mismatch")

    settings = get_settings()

    token = await exchange_code_for_token(
        client_id=settings.spotify_client_id,
        client_secret=settings.spotify_client_secret,
        redirect_uri=settings.spotify_redirect_uri,
        code=code,
    )

    me = await spotify_get(token["access_token"], "/me")
    spotify_user_id = me.get("id")
    if not spotify_user_id:
        raise HTTPException(status_code=500, detail="Could not read Spotify user id from /me")

    save_token(settings.token_dir, spotify_user_id, token)

    resp = RedirectResponse(url="/me")
    resp.delete_cookie(STATE_COOKIE)
    resp.set_cookie(USER_COOKIE, spotify_user_id, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 30)
    return resp

def _require_user_id(request: Request) -> str:
    uid = request.cookies.get(USER_COOKIE)
    if not uid:
        raise HTTPException(status_code=401, detail="Not logged in. Go to /auth/login")
    return uid

@app.get("/me")
async def me(request: Request):
    settings = get_settings()
    uid = _require_user_id(request)

    token = load_token(settings.token_dir, uid)
    if not token or "access_token" not in token:
        raise HTTPException(status_code=401, detail="Token missing for this user. Login again.")

    return await spotify_get(token["access_token"], "/me")

@app.get("/auth/refresh")
async def auth_refresh(request: Request):
    settings = get_settings()
    uid = _require_user_id(request)

    token = load_token(settings.token_dir, uid)
    if not token or "refresh_token" not in token:
        raise HTTPException(status_code=401, detail="No refresh token saved. Login again.")

    new_tok = await refresh_access_token(
        settings.spotify_client_id,
        settings.spotify_client_secret,
        token["refresh_token"],
    )
    if "refresh_token" not in new_tok:
        new_tok["refresh_token"] = token["refresh_token"]

    save_token(settings.token_dir, uid, new_tok)
    return {"ok": True}

@app.get("/auth/logout")
def logout(request: Request):
    settings = get_settings()
    uid = request.cookies.get(USER_COOKIE)

    if uid:
        delete_token(settings.token_dir, uid)

    resp = RedirectResponse(url="/")
    resp.delete_cookie(USER_COOKIE)
    return resp

@app.get("/")
def root():
    return {"message": "spotifeel backend running", "try": ["/docs", "/health", "/auth/login", "/me"]}

@app.get("/spotify/top-tracks")
async def top_tracks(request: Request, limit: int = 20, time_range: TimeRange = "medium_term"):
    settings = get_settings()
    uid = _require_user_id(request)

    token = load_token(settings.token_dir, uid)
    if not token or "access_token" not in token:
        raise HTTPException(status_code=401, detail="Token missing for this user. Login again.")

    params = {"limit": limit, "time_range": time_range}
    return await spotify_get(token["access_token"], "/me/top/tracks", params=params)


@app.get("/spotify/top-artists")
async def top_artists(request: Request, limit: int = 20, time_range: TimeRange = "medium_term"):
    settings = get_settings()
    uid = _require_user_id(request)

    token = load_token(settings.token_dir, uid)
    if not token or "access_token" not in token:
        raise HTTPException(status_code=401, detail="Token missing for this user. Login again.")

    params = {"limit": limit, "time_range": time_range}
    return await spotify_get(token["access_token"], "/me/top/artists", params=params)


@app.get("/spotify/recently-played")
async def recently_played(request: Request, limit: int = 20):
    settings = get_settings()
    uid = _require_user_id(request)

    token = load_token(settings.token_dir, uid)
    if not token or "access_token" not in token:
        raise HTTPException(status_code=401, detail="Token missing for this user. Login again.")

    params = {"limit": limit}
    return await spotify_get(token["access_token"], "/me/player/recently-played", params=params)