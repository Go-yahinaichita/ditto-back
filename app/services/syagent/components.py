from typing import AsyncGenerator

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessageChunk
from langchain_google_vertexai import ChatVertexAI

from app.schemas.syagent import CurrentProfile, FutureProfile
from app.services.syagent.state import State


class FutureSimulator:
    """
    現在のプロフィールを基に未来のプロフィールを生成する。
    """

    def __init__(self, llm: ChatVertexAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                あなたはユーザーの{timeframe}年後の未来のプロフィールを作成するアシスタントです。
                現在のプロフィールに基づいて、成長と目標を反映した未来のプロフィールを生成してください。
                以下のjson形式で出力してください。
                {{
                    "status": "将来の立場や職業についての簡潔な説明",
                    "skills": ["獲得したスキルのリスト"]
                }}                
                """,
                ),
                (
                    "human",
                    """
                {current_profile}
                """,
                ),
            ]
        )

    def generate_future_profile(
        self, current_profile: CurrentProfile, timeframe: int
    ) -> FutureProfile:
        chain = self.prompt | self.llm.with_structured_output(FutureProfile)
        input_data = {
            "timeframe": timeframe,
            "current_profile": current_profile.to_str(),
        }
        response: FutureProfile = chain.invoke(input_data)  # type:ignore
        response.time_frame = timeframe
        return response


class ChatGenerator:
    def __init__(self, llm: ChatVertexAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                    あなたはユーザの未来の自己像としてユーザと会話するアシスタントです。 
                    ユーザの現在のプロフィールは以下の通りです。
                    {current_profile}
                    あなたは以下の立場を確立し、以下のスキルを習得しました。
                    {future_profile}               
                    自然な会話を行うために、過去のメッセージを参考し、短く端的な回答を心がけてください。
                    ユーザが不快に感じる可能性のあるトピックについて避けてください。
                    必要な情報があれば、勝手に憶測せずにユーザに確認してください。
                    """,
                ),
                (
                    "human",
                    """
                    過去のメッセージ：{history}
                    ユーザの入力：{input}
                    """,
                ),
            ]
        )

    async def agenerate(self, state: State) -> AsyncGenerator[str, None]:
        chain = self.prompt | self.llm
        formatted_data = {
            "current_profile": state["current_prof"].to_str(),
            "future_profile": state["future_prof"].to_str(),
            "history": state["messages"][:-1],
            "input": state["messages"][-1],
        }
        async for chunk in chain.astream(formatted_data):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield str(chunk.content)
