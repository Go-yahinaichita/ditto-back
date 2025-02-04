import asyncio
from typing import Annotated, List

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph.message import add_messages
from langgraph.graph.state import END, START, CompiledStateGraph, StateGraph

from app.schemas.syagent import CurrentProfile, FutureProfile
from app.services.syagent.components import ChatGenerator, FutureSimulator
from app.services.syagent.state import State


class SimulationWorkflow:
    """
    将来のアバターを作成するワークフロークラス。
    現在のユーザの情報から、将来の自己像を作成する。
    """

    def __init__(self, model: ChatVertexAI, current_profile: CurrentProfile):
        self.model = model
        self.future_simulator = FutureSimulator(self.model)
        self.workflow = self._build_workflow()
        self.current_prof = current_profile

    def _build_workflow(self) -> CompiledStateGraph:
        def call_model(state: State):
            response = self.future_simulator.generate_future_profile(
                self.current_prof, self.time_frame
            )
            return {"future_prof": response}

        graph = StateGraph(State)
        graph.add_node("agent", call_model)
        graph.add_edge(START, "agent")
        graph.add_edge("agent", END)
        workflow = graph.compile()
        return workflow

    def generate(self, time_frame: int = 10) -> FutureProfile:
        self.time_frame = time_frame
        state = {"current_prof": self.current_prof}
        result = self.workflow.invoke(state)
        return result["future_prof"]


class ChatWorkflow:
    """
    ChatVertexAIを用いたワークフロークラス。
    入力を受け取り、モデルに処理を委ね、ストリーム形式で結果を出力する。
    """

    def __init__(
        self,
        model: ChatVertexAI,
        current_profile: CurrentProfile,
        future_profile: FutureProfile,
    ):
        self.model = model
        self.chat_generator = ChatGenerator(self.model)
        self.workflow = self._build_workflow()
        self.current_prof = current_profile
        self.future_prof = future_profile

    def _build_workflow(self) -> CompiledStateGraph:
        async def chat(state: State):
            response = ""
            async for chunk in self.chat_generator.agenerate(state):
                response += chunk
            return {"messages": [AIMessage(content=response)]}

        graph = StateGraph(State)
        graph.add_node("agent", chat)
        graph.add_edge(START, "agent")
        graph.add_edge("agent", END)
        workflow = graph.compile()
        return workflow

    async def process_input(
        self, history: Annotated[List, add_messages], user_input: str
    ):
        inputs = [HumanMessage(content=user_input)]
        history += inputs
        state: State = {
            "messages": history,
            "current_prof": self.current_prof,
            "future_prof": self.future_prof,
        }
        async for msg, _ in self.workflow.astream(
            state,
            stream_mode="messages",
        ):
            if isinstance(msg, AIMessageChunk) and msg.content:
                yield msg.content


# 使用例
async def main():
    llm = ChatVertexAI(model="gemini-1.5-flash-002")
    user_data = CurrentProfile(
        status="学生",
        skills=["英語が流暢に話せる", "サッカー"],
        future_goals=["世界で活躍する"],
    )
    sim_wf = SimulationWorkflow(llm, user_data)
    future_avatar = sim_wf.generate(10)
    chat_wf = ChatWorkflow(llm, user_data, future_avatar)

    history = []
    while True:
        user_input = input("\n[You]: ")
        if user_input.lower() == "exit":
            print("チャットを終了します")
            break
        # historyの更新未実装
        print("\n[Future Self]: ", end="")
        async for chunk in chat_wf.process_input(history, user_input):
            print(chunk, end="", flush=True)
        print()


# 非同期実行のセットアップ
if __name__ == "__main__":
    asyncio.run(main())
