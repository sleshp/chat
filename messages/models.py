import uuid
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Messages(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(ForeignKey("chats.id", ondelete="CASCADE"))
    sender_id = Column(ForeignKey("users.id", ondelete="CASCADE"))
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    client_msg_id = Column(UUID(as_uuid=True), nullable=False, unique=True)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")

    __table_args__ = (UniqueConstraint("client_msg_id", name="uq_messages_client_msg_id"),)