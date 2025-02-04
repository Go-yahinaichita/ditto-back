from fastapi import HTTPException
from langchain_google_vertexai import ChatVertexAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import syagent as syagent_model
from app.schemas import syagent as syagent_schema
from app.schemas import utils as utils_schema
from app.services.syagent import agents as syagent_service

llm = ChatVertexAI(model="gemini-1.5-flash-002")


async def read_conversations(
    db: AsyncSession, user_id: int
) -> list[syagent_schema.OutputConversation]:
    result = await db.execute(
        select(syagent_model.Conversation).filter_by(user_id=user_id)
    )
    conversations = result.scalars().all()
    if not conversations:
        return []
    return [
        syagent_schema.OutputConversation.model_validate(conversation)
        for conversation in conversations
    ]


async def create_conversation(
    db: AsyncSession, user_id: int, current_profile: syagent_schema.CurrentProfile
) -> syagent_schema.OutputConversation:
    # future_avatar作成
    sim_wf = syagent_service.SimulationWorkflow(llm, current_profile)
    future_profile = syagent_model.FutureAvatar(**sim_wf.generate().model_dump())
    db.add(future_profile)
    await db.flush()
    # conversation作成
    conversation = syagent_model.Conversation(
        user_id=user_id,
        future_avatar_id=future_profile.id,
        title="Conversation",
    )
    db.add(conversation)
    return syagent_schema.OutputConversation.model_validate(conversation)


async def read_messages(
    db: AsyncSession, conversation_id: int
) -> list[syagent_schema.OutputMessage]:
    result = await db.execute(
        select(syagent_model.Message).filter_by(conversation_id=conversation_id)
    )
    messages = result.scalars().all()
    if not messages:
        return []
    return [
        syagent_schema.OutputMessage.model_validate(message) for message in messages
    ]


async def create_message(
    db: AsyncSession, conversation_id: int, input_message: syagent_schema.InputMessage
) -> syagent_schema.OutputMessage:
    message = syagent_model.Message(
        conversation_id=conversation_id, role="user", **input_message.model_dump()
    )
    output_message = syagent_model.Message(
        conversation_id=conversation_id, role="agent", message="Hello!"
    )
    db.add(message)
    db.add(output_message)
    return syagent_schema.OutputMessage.model_validate(output_message)


async def delete_conversation(db: AsyncSession, conversation_id: int):
    result = await db.execute(
        select(syagent_model.Conversation).filter_by(id=conversation_id)
    )
    conversation = result.scalar()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conversation)
    return utils_schema.ResponseMessage(status=204, message="Conversation deleted")
