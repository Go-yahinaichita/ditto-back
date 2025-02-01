import asyncio
from typing import AsyncGenerator

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessageChunk
from langchain_google_vertexai import ChatVertexAI

from app.schemas.syagent import CurrentProfile, FutureProfile


class FutureSimulator:
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
        """
        現在のプロフィールを基に未来のプロフィールを生成する。
        """
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
                    あなたはユーザーの未来の自己像を描くアシスタントです。 
                    ユーザーの現在のプロフィールは
                    {current_profile}
                    あなたは以下の立場を確立し、以下のスキルを習得しました。
                    {future_profile}               
                    ユーザの未来の自己像になりすまして、ユーザと自然な会話を行ってください。
                    """,
                ),
                (
                    "human",
                    """
                {input}
                """,
                ),
            ]
        )

    async def agenerate(
        self,
        current_profile: CurrentProfile,
        future_profile: FutureProfile,
        user_input: str,
    ) -> AsyncGenerator[str, None]:
        chain = self.prompt | self.llm
        formatted_data = {
            "current_profile": current_profile.to_str(),
            "future_profile": future_profile.to_str(),
            "input": user_input,
        }
        async for chunk in chain.astream(formatted_data):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield str(chunk.content)


# 使用例
async def main():
    llm = ChatVertexAI(model="gemini-1.5-flash-002", temperature=0.7)
    simulator = FutureSimulator(llm)
    gen = ChatGenerator(llm)

    user_data = CurrentProfile(
        status="プログラミング初学者",
        skills=["Python基礎", "データ分析入門"],
        future_goals=["AIエンジニアとして活躍する"],
    )
    future_description = simulator.generate_future_profile(user_data, 10)
    print(future_description)

    while True:
        user_input = input("\n[You]: ")
        if user_input.lower() == "exit":
            print("Exiting the chat. Have a great day!")
            break

        print("\n[Future Self]: ", end="")
        async for chunk in gen.agenerate(user_data, future_description, user_input):
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
