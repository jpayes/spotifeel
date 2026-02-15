from fastapi import FastAPI
from spotifeel_api.routes.auth import router as auth_router
from spotifeel_api.routes.user_data import router as user_router

app = FastAPI(title="spotifeel api")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {
        "message": "spotifeel backend running",
        "try": ["/docs", "/health", "/auth/login", "/user/me", "/user/top-tracks"],
    }

# Routers
app.include_router(auth_router)
app.include_router(user_router)