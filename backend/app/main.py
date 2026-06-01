from fastapi import FastAPI

from app.core.settings import get_settings
from app.routers import projects

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)
app.include_router(projects.router)


@app.get("/")
def root():
    return {"message": "DraftHub API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
    }