from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.utils.mixin import TimestampMixin


class CurrentProfiles(Base, TimestampMixin):
    __tablename__ = "current_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    future_avatars: Mapped[list["FutureAvatars"]] = relationship(
        "FutureAvatars", back_populates="current_profile"
    )


class FutureAvatars(Base, TimestampMixin):
    __tablename__ = "future_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    current_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("current_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    current_profile: Mapped["CurrentProfiles"] = relationship(
        "CurrentProfiles", back_populates="future_avatars"
    )
    conversations: Mapped[list["Conversations"]] = relationship(
        "Conversations", back_populates="future_avatar"
    )


class Conversations(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    future_avatar_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("future_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    future_avatar: Mapped["FutureAvatars"] = relationship(
        "FutureAvatars", back_populates="conversations"
    )
    messages: Mapped[list["Messages"]] = relationship(
        "Messages", back_populates="conversation"
    )


class Messages(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    conversation: Mapped["Conversations"] = relationship(
        "Conversations", back_populates="messages"
    )
