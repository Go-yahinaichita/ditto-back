from pydantic import BaseModel


class ResponseMessage(BaseModel):
    """APIのレスポンス"""

    status: int
    message: str
