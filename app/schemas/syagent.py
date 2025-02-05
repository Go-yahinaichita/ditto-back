from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OutputConversation(BaseModel):
    """会話の情報"""

    id: int = Field(..., description="会話のID")
    title: str = Field(..., description="会話のタイトル")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    model_config = ConfigDict(from_attributes=True)


class InputMessage(BaseModel):
    """メッセージの入力情報"""

    message: str = Field(..., description="メッセージの内容")


class OutputMessage(BaseModel):
    """メッセージの出力情報"""

    id: int = Field(..., description="メッセージのID")
    role: Literal["user", "agent"] = Field(
        ..., description="メッセージの役割（ユーザーかエージェントか）"
    )
    message: str = Field(..., description="メッセージの内容")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    model_config = ConfigDict(from_attributes=True)


class RoleMessage(BaseModel):
    """役割付きメッセージ"""

    role: Literal["user", "agent"] = Field(..., description="メッセージの役割")
    content: str = Field(..., description="メッセージの内容")


class CurrentProfile(BaseModel):
    """現在のプロフィールの入力情報"""

    age: int = Field(..., description="年齢")
    restrictions: str = Field(..., description="経済面、環境面での制約")
    values: str = Field(..., description="価値観")

    status: str = Field(..., description="現在の立場や職業")
    skills: list[str] = Field(..., description="現在持っているスキルのリスト")
    future_goals: list[str] = Field(..., description="将来の目標ややりたいことのリスト")

    extra: str = Field(..., description="補足、追加情報")

    def to_str(self):
        return (
            f"現在のプロフィール:\n"
            f"- 年齢: {self.age}\n"
            f"- 制約: {self.restrictions}\n"
            f"- 価値観: {self.values}\n"
            f"- 現在の立場や職業: {self.status}\n"
            f"- 現在持っているスキル: {', '.join(self.skills)}\n"
            f"- 将来の目標: {', '.join(self.future_goals)}\n"
            f"- 補足: {self.extra}"
        )


class FutureProfile(BaseModel):
    """シミュレートした将来のプロフィール情報"""

    status: str = Field(..., description="未来の立場や職業")
    skills: list[str] = Field(
        ..., description="未来において持つと想定されるスキルのリスト"
    )
    time_frame: int = Field(
        10, ge=1, le=50, description="未来像を描くための期間（年単位）"
    )
    summary: str = Field(..., description="プロフィールの要約")

    def to_str(self):
        return f" {self.time_frame}年後の立場や職業: {self.status}、{self.time_frame}年間で獲得したスキル:{', '.join(self.skills)}"


class ChatState(BaseModel):
    """LangGraphのステート"""

    messages: list[RoleMessage] = Field(..., description="チャット履歴")
    current_prof: CurrentProfile = Field(
        ..., description="ユーザーの現在のプロフィール情報"
    )
    future_prof: FutureProfile = Field(
        ..., description="シミュレートした将来のプロフィール情報"
    )
