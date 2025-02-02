from typing import List

from pydantic import BaseModel, Field


class CurrentProfile(BaseModel):
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
