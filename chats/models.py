import enum
import uuid

from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class ChatType(enum.Enum):
    personal = "personal"
    group = "group"


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    type = Column(Enum(ChatType), nullable=False)