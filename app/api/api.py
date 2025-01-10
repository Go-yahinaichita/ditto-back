from app.api.routers import chat

from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(chat.router)
