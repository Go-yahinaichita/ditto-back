import asyncio

from langchain_core.messages import AIMessageChunk, ToolMessage, AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph.state import END, START, CompiledStateGraph, StateGraph
from langgraph.prebuilt import ToolNode

from app.schemas.syagent import ChatState, CurrentProfile, FutureProfile, RoleMessage
from app.services.syagent.components import (
    ChatGenerator,
    FutureSimulator,
    ProfileGenerator,
)
from app.services.syagent.state import SimState
from app.services.syagent.tools import CareerTool


class SimulationWorkflow:
    """
    将来のアバターを作成するワークフロークラス。
    現在のユーザの情報から、将来の自己像を作成する。
    """

    def __init__(self, model: ChatVertexAI, current_profile: CurrentProfile):
        self.model = model
        self.model_with_tools = self._define_tools(model)
        self.future_simulator = FutureSimulator(self.model_with_tools)
        self.prof_generator = ProfileGenerator(self.model)

        self.workflow = self._build_workflow()
        self.current_prof = current_profile

    def _define_tools(self, model: ChatVertexAI):
        career_tool = CareerTool(model)

        @tool
        def design_career(
            time_frame: int,
            current_age: int,
            current_status: str,
            current_skills: list[str],
            values: str,
            restrictions: str,
            future_goals: list[str],
        ):
            """現在のプロフィールから、現実的なキャリアパスを提案"""
            current_prof = CurrentProfile(
                age=current_age,
                status=current_status,
                skills=current_skills,
                values=values,
                restrictions=restrictions,
                future_goals=future_goals,
                extra="",
            )
            response = career_tool.chain.invoke(
                {"time_frame": time_frame, "current_prof": current_prof}
            )
            return f"具体的なキャリアパスの一つは以下です。\n{response.content}"

        # skills_tool = RequiredSkillsTool(model)
        # @tool
        # def search_required_skills(future_goals: list[str]):
        #     """将来の目標に基づき、必要なスキルを取得"""
        #     response = skills_tool.chain.invoke({"future_goals": future_goals})
        #     return f"将来の目標達成に必要なスキルは以下です。\n{response.content}"

        self.tools = [design_career]
        return model.bind_tools(self.tools)

    def _build_workflow(self) -> CompiledStateGraph:
        def call_model(state: SimState):
            gathered_info = gathered_info = ", ".join(
                str(msg.content)
                for msg in state["messages"]
                if isinstance(msg, ToolMessage)
            )
            response = self.future_simulator.run(
                self.time_frame, self.current_prof, gathered_info
            )
            if response.tool_calls:
                return {"messages": response}
            else:
                profile = self.prof_generator.generate(
                    self.time_frame, self.current_prof, gathered_info
                )
                return {"future_profile": profile}

        def should_continue(state: SimState):
            messages = state["messages"]
            last_message = messages[-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return "tools"
            return END

        graph = StateGraph(SimState)
        tool_node = ToolNode(self.tools)
        graph.add_node("agent", call_model)
        graph.add_node("tools", tool_node)

        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", should_continue, ["tools", END])
        graph.add_edge("tools", "agent")
        workflow = graph.compile()
        return workflow

    def generate(self, time_frame: int = 10) -> FutureProfile:
        self.time_frame = time_frame
        future_prof = FutureProfile(
            status="", skills=[], time_frame=time_frame, summary=""
        )
        state = SimState(
            {"messages": [HumanMessage(content="")], "future_profile": future_prof}
        )
        result = self.workflow.invoke(state)
        return result["future_profile"]


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
        values="健康第一",
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
        print("\n[Future Self]: ", end="")
        res = ""
        async for chunk in chat_wf.process_input(history, user_input):
            print(chunk, end="", flush=True)
            res += str(chunk)
        history += [
            RoleMessage(role="user", content=user_input),
            RoleMessage(role="agent", content=res),
        ]


# 非同期実行のセットアップ
if __name__ == "__main__":
    asyncio.run(main())
