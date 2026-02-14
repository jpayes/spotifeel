import json
import os
from typing import Any, Dict, Optional

def _token_path(token_dir: str, spotify_user_id: str) -> str:
    safe = spotify_user_id.replace("/", "_")
    return os.path.join(token_dir, f"{safe}.json")

def save_token(token_dir: str, spotify_user_id: str, token: Dict[str, Any]) -> str:
    os.makedirs(token_dir, exist_ok=True)
    path = _token_path(token_dir, spotify_user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(token, f, indent=2)
    return path

def load_token(token_dir: str, spotify_user_id: str) -> Optional[Dict[str, Any]]:
    path = _token_path(token_dir, spotify_user_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def delete_token(token_dir: str, spotify_user_id: str) -> bool:
    path = _token_path(token_dir, spotify_user_id)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False