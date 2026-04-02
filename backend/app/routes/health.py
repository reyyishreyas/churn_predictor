from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/")
def root() -> dict:
    return {
        "message": f"{settings.app_name} is running",
        "version": settings.app_version,
        "docs": "/docs",
    }


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}
