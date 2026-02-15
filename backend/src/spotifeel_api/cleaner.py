def _best_image(images: list[dict]) -> str | None:
    if not images:
        return None
    return images[0].get("url")


def simplify_track(track: dict) -> dict:
    album = track.get("album", {}) or {}
    return {
        "id": track.get("id"),
        "name": track.get("name"),
        "artists": [a.get("name") for a in track.get("artists", []) if a.get("name")],
        "album": album.get("name"),
        "image": _best_image(album.get("images", [])),
        "duration_ms": track.get("duration_ms"),
        "explicit": track.get("explicit"),
        "url": (track.get("external_urls") or {}).get("spotify"),
        "uri": track.get("uri")
    }


def simplify_artist(artist: dict) -> dict:
    return {
        "id": artist.get("id"),
        "name": artist.get("name"),
        "genres": artist.get("genres", []),
        "popularity": artist.get("popularity"),
        "followers": (artist.get("followers") or {}).get("total"),
        "image": _best_image(artist.get("images", [])),
        "url": (artist.get("external_urls") or {}).get("spotify"),
        "uri": artist.get("uri")
    }


def simplify_recent_item(item: dict) -> dict:
    track = item.get("track") or {}
    return {
        "played_at": item.get("played_at"),
        "track": simplify_track(track)
    }