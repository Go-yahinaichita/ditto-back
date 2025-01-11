from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.utils.mixin import TimestampMixin


class Chats(Base, TimestampMixin):
    __tablename__ = "chats"

    id: Mapped[BigInteger] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String)
    Messages: Mapped[list["Messages"]] = relationship("Messages", back_populates="chat")


class Messages(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[BigInteger] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    chat_id: Mapped[BigInteger] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    input_message: Mapped[str] = mapped_column(String)
    output_message: Mapped[str] = mapped_column(String)
    chat: Mapped[Chats] = relationship("Chats", back_populates="Messages")
