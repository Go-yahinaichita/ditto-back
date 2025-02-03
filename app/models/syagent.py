from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.utils.mixin import TimestampMixin


class CurrentProfile(Base, TimestampMixin):
    __tablename__ = "current_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    future_avatars: Mapped["FutureAvatar"] = relationship(
        "FutureAvatar", back_populates="current_profile"
    )


class FutureAvatar(Base, TimestampMixin):
    __tablename__ = "future_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    current_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("current_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    current_profile: Mapped["CurrentProfile"] = relationship(
        "CurrentProfile", back_populates="future_avatar"
    )
    conversations: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="future_avatar"
    )


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    future_avatar_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("future_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    future_avatar: Mapped["FutureAvatar"] = relationship(
        "FutureAvatar", back_populates="conversation"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation"
    )


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String, nullable=False)  # TODO: Enum
    Message: Mapped[str] = mapped_column(String, nullable=False)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="message"
    )
