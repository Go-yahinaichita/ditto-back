from typing import List
from pydantic import BaseModel, Field

class CurrentProfile(BaseModel):
    status: str =Field(..., description="現在の状況や立場")
    skills: List[str] = Field(..., description="現在持っているスキルのリスト")
    future_goals: List[str] = Field(..., description="将来の目標ややりたいことのリスト")

class FutureProfile(BaseModel):
    status: str = Field(..., description="未来の状況や立場")
    skills: List[str] = Field(...,description="未来において持つと想定されるスキルのリスト")
    time_frame: int = Field(10, ge=1, le=50,description="未来像を描くための期間（年単位）")