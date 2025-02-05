import asyncio

from langchain_core.messages import AIMessageChunk
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph.state import END, START, CompiledStateGraph, StateGraph

from app.schemas.syagent import ChatState, CurrentProfile, FutureProfile, RoleMessage
from app.services.syagent.components import ChatGenerator, FutureSimulator


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
        self.chat_state = ChatState(
            messages=[],
            current_prof=current_profile,
            future_prof=FutureProfile(status="", skills=[], time_frame=10, summary=""),
        )

    def _build_workflow(self) -> CompiledStateGraph:
        def call_model(state: ChatState):
            response = self.future_simulator.generate_future_profile(state)
            return {"future_prof": response}

        graph = StateGraph(ChatState)
        graph.add_node("agent", call_model)
        graph.add_edge(START, "agent")
        graph.add_edge("agent", END)
        workflow = graph.compile()
        return workflow

    def generate(self, time_frame: int = 10) -> FutureProfile:
        self.chat_state.future_prof.time_frame = time_frame
        result = self.workflow.invoke(self.chat_state)
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
        async def chat(state: ChatState):
            response = ""
            async for chunk in self.chat_generator.agenerate(state):
                response += chunk
            state.messages += [RoleMessage(role="agent", content=response)]
            return state

        graph = StateGraph(ChatState)
        graph.add_node("agent", chat)
        graph.add_edge(START, "agent")
        graph.add_edge("agent", END)
        workflow = graph.compile()
        return workflow

    async def process_input(self, history: list[RoleMessage], user_input: str):
        input = history + [RoleMessage(role="user", content=user_input)]
        state: ChatState = ChatState(
            messages=input,
            current_prof=self.current_prof,
            future_prof=self.future_prof,
        )
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
        age=20,
        restrictions="親の面倒を見る必要がある",
        values="家族を大切にしたい",
        status="学生",
        skills=["英語が流暢に話せる", "サッカー"],
        future_goals=["世界で活躍する"],
        extra="",
    )
    sim_wf = SimulationWorkflow(llm, user_data)
    future_avatar = sim_wf.generate(10)
    print(future_avatar)
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


# 非同期実行のセットアップ
if __name__ == "__main__":
    asyncio.run(main())
