import uuid

from sqlalchemy import Column, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class Messages(Base):
    __tablename__ = 'messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="Cascade"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="Cascade"), nullable=False)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)
