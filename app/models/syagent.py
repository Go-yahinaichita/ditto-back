from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.utils.mixin import TimestampMixin


class CurrentProfile(Base, TimestampMixin):
    __tablename__ = "current_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    age: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    values: Mapped[str] = mapped_column(String, nullable=False)
    restrictions: Mapped[str] = mapped_column(String, nullable=False)
    extra: Mapped[str] = mapped_column(String, nullable=False)
    future_profile: Mapped["FutureProfile"] = relationship(
        "FutureProfile", back_populates="current_profile", cascade="all, delete-orphan"
    )
    current_skills: Mapped[list["CurrentSkill"]] = relationship(
        "CurrentSkill", back_populates="current_profile", cascade="all, delete-orphan"
    )
    future_goals: Mapped[list["FutureGoal"]] = relationship(
        "FutureGoal", back_populates="current_profile", cascade="all, delete-orphan"
    )


class FutureProfile(Base, TimestampMixin):
    __tablename__ = "future_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    current_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("current_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    status: Mapped[str] = mapped_column(String, nullable=False)
    time_frame: Mapped[int] = mapped_column(BigInteger, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    current_profile: Mapped["CurrentProfile"] = relationship(
        "CurrentProfile", back_populates="future_profile"
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="future_profile", cascade="all, delete-orphan"
    )
    future_skills: Mapped[list["FutureSkill"]] = relationship(
        "FutureSkill", back_populates="future_profile", cascade="all, delete-orphan"
    )


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)  # Firebase uid
    future_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("future_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    future_profile: Mapped["FutureProfile"] = relationship(
        "FutureProfile", back_populates="conversation"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String, nullable=False)  # TODO: Enum
    message: Mapped[str] = mapped_column(String, nullable=False)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )


class CurrentSkill(Base, TimestampMixin):
    __tablename__ = "current_skills"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    current_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("current_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill: Mapped[str] = mapped_column(String, nullable=False)
    current_profile: Mapped["CurrentProfile"] = relationship(
        "CurrentProfile", back_populates="current_skills"
    )


class FutureSkill(Base, TimestampMixin):
    __tablename__ = "future_skills"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    future_profile_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("future_profiles.id", ondelete="CASCADE"), nullable=False
    )
    skill: Mapped[str] = mapped_column(String, nullable=False)
    future_profile: Mapped["FutureProfile"] = relationship(
        "FutureProfile", back_populates="future_skills"
    )


class FutureGoal(Base, TimestampMixin):
    __tablename__ = "future_goals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    current_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("current_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    goal: Mapped[str] = mapped_column(String, nullable=False)
    current_profile: Mapped["CurrentProfile"] = relationship(
        "CurrentProfile", back_populates="future_goals"
    )
