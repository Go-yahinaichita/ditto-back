import asyncio
from typing import Dict, Any, AsyncGenerator
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessageChunk

from app.schemas.syagent import CurrentProfile, FutureProfile



class FutureSimulator:
    def __init__(self, llm: ChatVertexAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate([
            ("system",
                """
                You are an assistant helping to envision {timeframe} years into the future.
                Based on the following current profile, generate a future profile that reflects the individual's growth and achievement of their goals.
                Respond with a JSON format:
                {{
                    "status": "A brief description of the future state",
                    "skills": ["A list of new skills acquired in the future"]
                }}                
                """,
            ),
            ("human",
                """
                Current Status: {current_status}
                Skills: {skills}
                Future Goals: {future_goals}
                """,
            ),
        ])

    def generate_future_profile(self, current_profile: CurrentProfile, timeframe: int) -> FutureProfile:
        """
        現在のプロフィールを基に未来のプロフィールを生成する。
        """
        chain = self.prompt|self.llm.with_structured_output(FutureProfile)
        input_data = {
            "timeframe":timeframe,
            "current_status": current_profile.status,
            "skills": ", ".join(current_profile.skills),
            "future_goals": current_profile.future_goals,
        }
        response :FutureProfile = chain.invoke(input_data) #type:ignore
        return response
    
class ChatGenerator:
    def __init__(self, llm: ChatVertexAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                ("system",
                    """
                    You are the user's future self. 
                    The user's current profile is listed below
                    Current status: {current_status}
                    Current skills: {current_skills}
                    Future goals: {future_goals}
                    You have achieved the following goals and mastered the skills listed below.               
                    Your current status: {future_status}
                    Your acquired skills: {future_skills}
                    reply in Japanese
                    """,
                ),
                ("human",
                """
                {input}
                """,
                ),
            ]
        )

    async def agenerate(self, current_profile: CurrentProfile, future_profile : FutureProfile ,user_input:str) -> AsyncGenerator[str, None]:
        chain = self.prompt| self.llm
        formatted_data = {
            "current_status":current_profile.status,
            "current_skills" :", ".join(current_profile.skills),
            "future_goals" :",".join(current_profile.future_goals),
            "future_status" :future_profile.status,
            "future_skills" :", ".join(future_profile.skills),
            "input": user_input,
        }
        async for chunk in chain.astream(formatted_data):
                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    yield str(chunk.content)

# 使用例
async def main():
    llm = ChatVertexAI(model = "gemini-1.5-flash-002",temperature=0.7)
    simulator = FutureSimulator(llm)
    gen = ChatGenerator(llm)

    user_data = CurrentProfile(
        status= "プログラミング初学者",
        skills = ["Python基礎", "データ分析入門"],
        future_goals = ["AIエンジニアとして活躍する"]
    )
    future_description = simulator.generate_future_profile(user_data,10)
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