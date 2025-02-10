from langchain.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI


class RequiredSkillsTool:
    def __init__(self, llm: ChatVertexAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                あなたは、ユーザが目標を達成するために必要なスキルや経験をアドバイスするアシスタントです。
                ユーザの将来の目標をもとに、それを達成するために必要不可欠なスキルや経験を答えてください。
                理由を述べる必要はありません。
                以下の形式で答えてください。
                必要不可欠なスキル：(一覧)
                """,
                ),
                (
                    "human",
                    """
                ユーザの将来の目標：{future_goals}
                """,
                ),
            ]
        )
        self.chain = self.prompt | self.llm


class CareerTool:
    def __init__(self, llm: ChatVertexAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                あなたは、ユーザが目標を達成するための道のりを考えるアシスタントです。
                ユーザの将来の目標をもとに、それを達成するためのキャリア設計を行ってください。
                年齢、制限、価値観を考慮したうえで現在から{time_frame}年分のキャリア設計を行ってください。
                キャリア設計はできるだけ簡潔に記述してください。
                """,
                ),
                (
                    "human",
                    """
                {current_prof}
                """,
                ),
            ]
        )
        self.chain = self.prompt | self.llm


class PotentialTool:
    def __init__(self, llm: ChatVertexAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                あなたはユーザが{time_frame}年後に目標を達成可能であるかを判断するアシスタントです。
                現在のプロフィールに基づいて、成長を考慮した上で、目標が達成可能かを判断してください。
                その結果と、その理由を以下の形式で出力してください。
                "結果":(0から100までの数値、100が容易に達成可能、0が達成することは非常に困難)
                "理由"：なぜそのような判断をしたかの短い説明         
                """,
                ),
                (
                    "human",
                    """
                {current_prof}
                """,
                ),
            ]
        )
        self.chain = self.prompt | self.llm
