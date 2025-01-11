from typing import AsyncGenerator

from langchain.schema.runnable import Runnable
from sqlalchemy.ext.asyncio import AsyncSession

import app.schemas.chat as chat_schema
from app.crud.chat import create_message

# TODO: ちょっと自信ない（トランザクション）


async def message_streamer(
    chat_id: int,
    input_message: chat_schema.InputMessage,
    session: AsyncSession,
    runnable: Runnable,
) -> AsyncGenerator[str, None]:
    full_message = ""
    async for chunk in runnable.astream({"question": input_message}):
        # chunkを受け取り、連結する
        full_message += chunk
        yield chunk

    # メッセージを作成
    message_create = chat_schema.CreateMessage(
        chat_id=chat_id,
        input_message=input_message.input_message,
        output_message=full_message,
    )
    await create_message(session, message_create)
