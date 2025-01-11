from datetime import datetime

from pydantic import BaseModel, Field


class CreateChat(BaseModel):
    title: str = Field(..., description="Chat title")


class ResponseChat(CreateChat):
    id: int = Field(..., description="Chat id")
    created_at: datetime = Field(..., description="Chat creation date")

    class Config:
        from_attributes = True


class InputMessage(BaseModel):
    input_message: str = Field(..., description="Chat message", examples=["Hello"])


class CreateMessage(InputMessage):
    chat_id: int = Field(..., description="Chat id")
    output_message: str = Field(
        ..., description="Chat response message", examples=["Hi"]
    )


class ResponseMessage(CreateMessage):
    id: int = Field(..., description="Message id")
    created_at: datetime = Field(..., description="Message creation date")

    class Config:
        from_attributes = True
