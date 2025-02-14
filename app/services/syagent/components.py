from typing import AsyncGenerator

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_google_vertexai import ChatVertexAI

from app.schemas.syagent import ChatState, CurrentProfile, FutureProfile


class Interviewer:
    def __init__(self, llm: ChatVertexAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                あなたは、ユーザの情報からユーザの未来像の予測に協力するインタビュアです。
                ユーザの未来像を正確に予測するために必要な情報をユーザに質問してください。
                必ず質問は1つのみ行ってください。             
                """,
                ),
                (
                    "human",
                    """
                現在のユーザの情報は以下の通りです。 
                {current_profile}
                """,
                ),
            ]
        )

    def generate_question(self, current_profile: CurrentProfile) -> str:
        chain = self.prompt | self.llm
        input_data = {
            "current_profile": current_profile.to_str(),
        }
        response: str = chain.invoke(input_data).content  # type:ignore
        return response


class FutureSimulator:
    """
    現在のプロフィールを基に未来のプロフィールを生成する。
    """

    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                あなたはユーザの{time_frame}年後の未来のプロフィールを作成するアシスタントです。
                これまでに集められた情報を確認し、追加の情報が必要な場合は適切なツールを呼び出してください。
                十分な情報が集まっている場合はツールを呼び出さずに、「情報収集完了」のみ出力してください。        
                """,
                ),
                (
                    "human",
                    """
                現在入手している情報：
                {current_profile}
                {gathered_info}
                """,
                ),
            ]
        )

    def run(
        self, time_frame: int, current_prof: CurrentProfile, gathered_info: str
    ) -> AIMessage:
        chain = self.prompt | self.llm
        input_data = {
            "time_frame": time_frame,
            "current_profile": current_prof.to_str(),
            "gathered_info": gathered_info,
        }
        response = chain.invoke(input_data)
        return response


class ProfileGenerator:
    """
    情報をもとに未来のプロフィールを生成する。
    """

    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                あなたはユーザーの{time_frame}年後の未来のプロフィールを作成する専門家です。
                現在のプロフィールとその他の情報に基づいて、成長と目標を反映した未来のプロフィールを生成してください。
                summaryの項目は生成したプロフィールの立場、職業を10~20文字程度で要約してください。               
                """,
                ),
                (
                    "human",
                    """
                {current_profile}
                追加情報：{gathered_info}
                """,
                ),
            ]
        )

    def generate(
        self, time_frame: int, current_prof: CurrentProfile, gathered_info: str
    ) -> FutureProfile:
        chain = self.prompt | self.llm.with_structured_output(FutureProfile)
        input_data = {
            "time_frame": time_frame,
            "current_profile": current_prof.to_str(),
            "gathered_info": gathered_info,
        }
        response: FutureProfile = chain.invoke(input_data)
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

    async def agenerate(self, state: ChatState) -> AsyncGenerator[str, None]:
        chain = self.prompt | self.llm
        formatted_data = {
            "current_profile": state.current_prof.to_str(),
            "future_profile": state.future_prof.to_str(),
            "history": state.messages[:-1],
            "input": state.messages[-1],
        }
        async for chunk in chain.astream(formatted_data):
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield str(chunk.content)
