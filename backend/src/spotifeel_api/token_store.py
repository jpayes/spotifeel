import json
import os
from typing import Any, Dict, Optional


def _token_path(token_dir: str, spotify_user_id: str) -> str:
    """Builds the full file path where a user's token will be stored.

    Args:
        token_dir (str): Directory where all token files are saved.
        spotify_user_id (str): The unique Spotify user ID.

    Returns:
        str: Full path to the user's token JSON file.
    """
    safe = spotify_user_id.replace("/", "_")
    return os.path.join(token_dir, f"{safe}.json")


def save_token(token_dir: str, spotify_user_id: str, token: Dict[str, Any]) -> str:
    """Saves a user's Spotify token data to a JSON file on disk.

    Args:
        token_dir (str): Directory where token files are stored.
        spotify_user_id (str): The unique Spotify user ID.
        token (Dict[str, Any]): Token data returned from Spotify (access + refresh tokens).

    Returns:
        str: Path to the saved token file.
    """
    os.makedirs(token_dir, exist_ok=True)
    path = _token_path(token_dir, spotify_user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(token, f, indent=2)
    return path


def load_token(token_dir: str, spotify_user_id: str) -> Optional[Dict[str, Any]]:
    """Loads a user's Spotify token data from disk.

    Args:
        token_dir (str): Directory where token files are stored.
        spotify_user_id (str): The unique Spotify user ID.

    Returns:
        Optional[Dict[str, Any]]: Token dictionary if it exists, otherwise None.
    """
    path = _token_path(token_dir, spotify_user_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_token(token_dir: str, spotify_user_id: str) -> bool:
    """Deletes a user's token file from disk.

    Args:
        token_dir (str): Directory where token files are stored.
        spotify_user_id (str): The unique Spotify user ID.

    Returns:
        bool: True if the token file was deleted, False if it did not exist.
    """
    path = _token_path(token_dir, spotify_user_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False