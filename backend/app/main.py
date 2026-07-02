from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.settings import get_settings
from app.routers import auth, blueprints, members, projects

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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