from fastapi import APIRouter

from app.api.routers.syagent import router as syagent

api_router = APIRouter()

api_router.include_router(syagent)
