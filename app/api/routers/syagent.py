from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import syagent as syagent_schema
from app.schemas import utils as utils_schema

router = APIRouter(prefix="/agents", tags=["agents"])


# /agents/{user_id} に対するエンドポイントを定義
@router.get("/{user_id}", response_model=syagent_schema.CurrentProfile)
async def get_conversations(user_id: int, db: AsyncSession = Depends(get_db)):
    pass


@router.post("/{user_id}", response_model=syagent_schema.OutputConversation)
async def post_conversation(
    user_id: int,
    current_profile: syagent_schema.CurrentProfile,
    db: AsyncSession = Depends(get_db),
):
    pass


# /agents/conversations/{conversation_id} に対するエンドポイントを定義
@router.get(
    "/conversations/{conversation_id}",
    response_model=list[syagent_schema.OutputMessage],
)
async def get_messages(conversation_id: int, db: AsyncSession = Depends(get_db)):
    pass


@router.post(
    "/conversations/{conversation_id}", response_model=syagent_schema.OutputMessage
)
async def post_message(
    conversation_id: int,
    input_message: syagent_schema.InputMessage,
    db: AsyncSession = Depends(get_db),
):
    pass


@router.delete(
    "/conversations/{conversation_id}", response_model=utils_schema.ResponseMessage
)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):
    pass
