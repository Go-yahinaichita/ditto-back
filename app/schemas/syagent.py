from datetime import datetime
from typing import List

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
    message: str = Field(..., description="メッセージの内容")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    model_config = ConfigDict(from_attributes=True)


class CurrentProfile(BaseModel):
    """現在のプロフィールの入力情報"""

    status: str = Field(..., description="現在の状況や立場")
    skills: List[str] = Field(..., description="現在持っているスキルのリスト")
    future_goals: List[str] = Field(..., description="将来の目標ややりたいことのリスト")

    def to_str(self):
        return f" 現在の立場や職業: {self.status}、現在持っているスキル: {', '.join(self.skills)}、将来の目標: {', '.join(self.future_goals)}"


class FutureProfile(BaseModel):
    status: str = Field(..., description="未来の状況や立場")
    skills: List[str] = Field(
        ..., description="未来において持つと想定されるスキルのリスト"
    )
    time_frame: int = Field(
        10, ge=1, le=50, description="未来像を描くための期間（年単位）"
    )

    def to_str(self):
        return f" {self.time_frame}年後の立場や職業: {self.status}、{self.time_frame}年間で獲得したスキル:{', '.join(self.skills)}"
