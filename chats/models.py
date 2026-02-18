import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class ChatType(enum.Enum):
    personal = "personal"
    group = "group"


class ParticipantRole(enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    type = Column(
        Enum(ChatType, name="chattype", native_enum=True, create_type=True),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    participants = relationship(
        "ChatParticipant", back_populates="chat", cascade="all, delete-orphan"
    )
    messages = relationship(
        "Messages", back_populates="chat", cascade="all, delete-orphan"
    )


class ChatParticipant(Base):
    __tablename__ = "chat_participants"
    __table_args__ = (
        UniqueConstraint(
            "chat_id", "user_id", name="uq_chat_participants_chat_id_user_id"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(ForeignKey("chats.id", ondelete="CASCADE"))
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(
        Enum(
            ParticipantRole, name="participantrole", native_enum=True, create_type=True
        ),
        nullable=False,
        default=ParticipantRole.member,
    )

    chat = relationship("Chat", back_populates="participants")
    user = relationship("User", back_populates="chats")
