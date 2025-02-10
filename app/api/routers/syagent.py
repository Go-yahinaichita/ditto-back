from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import syagent as syagent_crud
from app.db.session import get_db
from app.schemas import syagent as syagent_schema
from app.schemas import utils as utils_schema

router = APIRouter(prefix="/agents", tags=["agents"])


# /agents/{user_id} に対するエンドポイントを定義
@router.get("/{user_id}", response_model=list[syagent_schema.OutputConversation])
async def get_conversations(
    user_id: str, db: AsyncSession = Depends(get_db)
) -> list[syagent_schema.OutputConversation]:
    return await syagent_crud.read_conversations(db, user_id)


@router.post("/{user_id}", response_model=syagent_schema.OutputConversation)
async def post_conversation(
    user_id: str,
    current_profile: syagent_schema.CurrentProfile,
    db: AsyncSession = Depends(get_db),
) -> syagent_schema.OutputConversation:
    return await syagent_crud.create_conversation(db, user_id, current_profile)


# /agents/conversations/{conversation_id} に対するエンドポイントを定義
@router.get(
    "/conversations/{conversation_id}",
    response_model=list[syagent_schema.OutputMessage],
)
async def get_messages(conversation_id: int, db: AsyncSession = Depends(get_db)):
    return await syagent_crud.read_messages(db, conversation_id)


@router.post(
    "/conversations/{conversation_id}", response_model=syagent_schema.OutputMessage
)
async def post_message(
    conversation_id: int,
    input_message: syagent_schema.InputMessage,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    output_message = await syagent_crud.create_message(
        db, conversation_id, input_message
    )

    async def stream_messages():
        for message in output_message:
            yield message

    return StreamingResponse(stream_messages(), media_type="text/event-stream")


@router.delete(
    "/conversations/{conversation_id}", response_model=utils_schema.ResponseMessage
)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await syagent_crud.delete_conversation(db, conversation_id)
