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
    db: AsyncSession, user_id: str
) -> list[syagent_schema.OutputConversation]:
    """
    ユーザが持つ会話のリストを取得する。
    """
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
    db: AsyncSession, user_id: str, current_profile: syagent_schema.CurrentProfile
) -> syagent_schema.OutputConversation:
    """
    ユーザの情報から、将来の自己像を生成し、会話を開始する。
    """
    # CurrentProfile 作成
    current_profile_model = syagent_model.CurrentProfile(
        user_id=user_id,
        age=current_profile.age,
        status=current_profile.status,
        values=current_profile.values,
        restrictions=current_profile.restrictions,
        extra=current_profile.extra,
    )
    db.add(current_profile_model)
    await db.flush()

    # CurrentSkill, FutureGoal 作成
    # スキルの登録
    current_skills = [
        syagent_model.CurrentSkill(
            current_profile_id=current_profile_model.id, skill=skill
        )
        for skill in current_profile.skills
    ]
    for skill in current_skills:
        db.add(skill)

    # 目標の登録
    future_goals = [
        syagent_model.FutureGoal(current_profile_id=current_profile_model.id, goal=goal)
        for goal in current_profile.future_goals
    ]
    for goal in future_goals:
        db.add(goal)

    # FutureProfile 作成
    # シミュレーションワークフローにより将来の自己像を生成
    sim_wf = syagent_service.SimulationWorkflow(llm, current_profile)
    generated_future_profile = sim_wf.generate()
    future_profile = syagent_model.FutureProfile(
        user_id=user_id,
        current_profile_id=current_profile_model.id,
        status=generated_future_profile.status,
        time_frame=generated_future_profile.time_frame,
        summary=generated_future_profile.summary,
    )
    db.add(future_profile)
    await db.flush()  # future_profile.id が取得可能になる

    # FutureSkill 作成
    future_skills = [
        syagent_model.FutureSkill(future_profile_id=future_profile.id, skill=skill)
        for skill in generated_future_profile.skills
    ]
    for skill in future_skills:
        db.add(skill)

    # Conversation 作成
    conversation = syagent_model.Conversation(
        user_id=user_id,
        future_profile_id=future_profile.id,
        title=future_profile.summary,
    )
    db.add(conversation)
    await db.flush()

    # Pydantic スキーマに変換して返却
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
) -> list[str]:
    # conversation取得
    conversation_result = await db.execute(
        select(syagent_model.Conversation).filter_by(id=conversation_id)
    )
    conversation = conversation_result.scalar()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # messages取得
    messages_result = await db.execute(
        select(syagent_model.Message).filter_by(conversation_id=conversation_id)
    )
    messages = messages_result.scalars().all()
    if not messages:
        messages = []

    # future_profile取得
    future_profile_result = await db.execute(
        select(syagent_model.FutureProfile).filter_by(id=conversation.future_profile_id)
    )
    future_profile = future_profile_result.scalar()
    if not future_profile:
        raise HTTPException(status_code=404, detail="Futureprofile not found")
    # future_skills取得
    future_skills_result = await db.execute(
        select(syagent_model.FutureSkill).filter_by(future_profile_id=future_profile.id)
    )
    future_skills = future_skills_result.scalars().all()
    if not future_skills:
        future_skills = []

    # current_profile取得
    current_profile_result = await db.execute(
        select(syagent_model.CurrentProfile).filter_by(
            id=future_profile.current_profile_id
        )
    )
    current_profile = current_profile_result.scalar()
    if not current_profile:
        raise HTTPException(status_code=404, detail="CurrentProfile not found")
    # current_skills取得
    current_skills_result = await db.execute(
        select(syagent_model.CurrentSkill).filter_by(
            current_profile_id=current_profile.id
        )
    )
    current_skills = current_skills_result.scalars().all()
    if not current_skills:
        current_skills = []
    # future_goals取得
    future_goals_result = await db.execute(
        select(syagent_model.FutureGoal).filter_by(
            current_profile_id=current_profile.id
        )
    )
    future_goals = future_goals_result.scalars().all()
    if not future_goals:
        future_goals = []

    # chat_workflow
    chat_wf = syagent_service.ChatWorkflow(
        llm,
        syagent_schema.CurrentProfile(
            age=current_profile.age,  ###Placeholder
            status=current_profile.status,
            skills=[skill.skill for skill in current_skills] if current_skills else [],
            values=current_profile.values,  ###Placeholder
            restrictions=current_profile.restrictions,  ###Placeholder
            future_goals=[goal.goal for goal in future_goals] if future_goals else [],
            extra=current_profile.extra,  ###Placeholder
        ),
        syagent_schema.FutureProfile(
            status=future_profile.status,
            time_frame=future_profile.time_frame,
            skills=[skill.skill for skill in future_skills] if future_skills else [],
            summary=future_profile.summary,  ###Placeholder
        ),
    )
    history = []
    if messages:
        for message in messages:
            if message.role == "user":
                history.append(
                    syagent_schema.RoleMessage(role="user", content=message.message)
                )
            elif message.role == "agent":
                history.append(
                    syagent_schema.RoleMessage(role="agent", content=message.message)
                )
    user_input = input_message.message
    st_message = ""
    streaming_messages: list[str] = []
    async for chunk in chat_wf.process_input(history, user_input):
        st_message += str(chunk)
        streaming_messages.append(str(chunk))
    message = syagent_model.Message(
        conversation_id=conversation_id, role="user", **input_message.model_dump()
    )
    output_message = syagent_model.Message(
        conversation_id=conversation_id, role="agent", message=st_message
    )
    db.add(message)
    db.add(output_message)
    return streaming_messages


async def delete_conversation(db: AsyncSession, conversation_id: int):
    result = await db.execute(
        select(syagent_model.Conversation).filter_by(id=conversation_id)
    )
    conversation = result.scalar()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conversation)
    return utils_schema.ResponseMessage(status=204, message="Conversation deleted")
