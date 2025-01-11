from fastapi import APIRouter

from app.api.routers import chat

api_router = APIRouter()

api_router.include_router(chat.router)
