from fastapi import APIRouter

from .churn import router as churn_router
from .health import router as health_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(churn_router, tags=["churn"])
