from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain.schema.runnable import Runnable
from sqlalchemy.ext.asyncio import AsyncSession

import app.schemas.chat as chat_schema
from app.crud.chat import create_chat, read_chat, read_chat_messages
from app.db.session import get_db
from app.services.chat.main import message_streamer
from app.services.chat.runnable import get_runnable

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/{chat_id}", response_model=chat_schema.ResponseChat)
async def get_chat(chat_id: int, session: AsyncSession = Depends(get_db)):
    return await read_chat(session, chat_id)


@router.post("/", response_model=chat_schema.ResponseChat)
async def post_chat(
    chat_create: chat_schema.CreateChat, session: AsyncSession = Depends(get_db)
):
    return await create_chat(session, chat_create)


@router.get("/{chat_id}/messages")
async def get_chat_messages(chat_id: int, session: AsyncSession = Depends(get_db)):
    return await read_chat_messages(session, chat_id)


@router.post("/{chat_id}/messages")
async def post_message(
    chat_id: int,
    input_message: chat_schema.InputMessage,
    runnable: Runnable = Depends(get_runnable),
    session: AsyncSession = Depends(get_db),
):
    return StreamingResponse(
        content=message_streamer(chat_id, input_message, session, runnable),
        media_type="text/event-stream",
    )
