from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import app.models.chat as chat_model
import app.schemas.chat as chat_schema


async def read_chat(db: AsyncSession, chat_id: int) -> chat_schema.ResponseChat:
    chat = await db.get(chat_model.Chats, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat_schema.ResponseChat.model_validate(chat)


async def create_chat(
    db: AsyncSession, chat_create: chat_schema.CreateChat
) -> chat_schema.ResponseChat:
    chat_data = chat_create.model_dump(exclude_unset=True)
    chat = chat_model.Chats(**chat_data)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat_schema.ResponseChat.model_validate(chat)


async def read_chat_messages(
    db: AsyncSession, chat_id: int
) -> list[chat_schema.ResponseMessage]:
    chat = await db.get(chat_model.Chats, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    result = await db.execute(
        select(chat_model.Messages).filter(chat_model.Messages.chat_id == chat_id)
    )
    messages = result.scalars().all()

    return [chat_schema.ResponseMessage.model_validate(message) for message in messages]


async def create_message(
    db: AsyncSession, message_create: chat_schema.CreateMessage
) -> None:
    chat = await db.get(chat_model.Chats, message_create.chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    message_data = message_create.model_dump(exclude_unset=True)
    message = chat_model.Messages(**message_data)
    db.add(message)
    await db.commit()
    await db.refresh(message)
