import uuid
from datetime import datetime

from pydantic import BaseModel


class MessageCreateSchema(BaseModel):
    chat_id: uuid.UUID
    text: str


class MessageReadSchema(BaseModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    sender_id: uuid.UUID
    text: str
    timestamp: datetime
    is_read: bool

    class Config:
        from_attributes = True
