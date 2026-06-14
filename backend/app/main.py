from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.settings import get_settings
from app.routers import auth, blueprints, members, projects

settings = get_settings()

# Rate limiter — limits by IP address
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(auth.router)
app.include_router(blueprints.router)
app.include_router(members.router)


@app.get("/")
def root():
    return {"message": "DraftHub API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
    }