import os
from dotenv import load_dotenv
from dataclasses import dataclass

# loads .env
load_dotenv()

# dataclass creates __init__, etc. (frozen js makes it read-only)
@dataclass(frozen=True)
class Settings:
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str
    token_dir: str = "backend/data/tokens"
    
    
# gets the values from .env file
def get_settings() -> Settings:
    client_id = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
    secret_id = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "").strip()
    
    # checks to see if any of the necessary values are missing
    missing = []
    if not client_id:
        missing.append("SPOTIFY_CLIENT_ID")
    if not secret_id:
        missing.append("SPOTIFY_CLIENT_SECRET")
    if not redirect_uri:
        missing.append("SPOTIFY_REDIRECT_URI")
    
    # error msg for missing .env vars
    if missing:
        raise RuntimeError(f"Missing .env variables: {', '.join(missing)}")
    
    return Settings(
        spotify_client_id=client_id,
        spotify_client_secret=secret_id,
        spotify_redirect_uri=redirect_uri
    )
    
