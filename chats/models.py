import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Enum, ForeignKey, DateTime
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
    __tablename__ = 'chats'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    type = Column(Enum(ChatType), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    participants = relationship("ChatParticipant", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("Messages", back_populates="chat", cascade="all, delete-orphan")


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(ForeignKey("chats.id", ondelete="CASCADE"))
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(Enum(ParticipantRole), nullable=False, default=ParticipantRole.member)

    chat = relationship("Chat", back_populates="participants")
    user = relationship("User", back_populates="chats")
