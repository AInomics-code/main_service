from fastapi import APIRouter

from rest.agents.routes import router as agents_router

router = APIRouter(prefix="/api/v1")

router.include_router(agents_router, tags=["Agents"])
