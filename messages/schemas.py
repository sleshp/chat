import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class MessageCreateSchema(BaseModel):
    chat_id: uuid.UUID
    text: str
    client_msg_id: uuid.UUID


class MessageReadSchema(BaseModel):
    id: uuid.UUID
    chat_id: uuid.UUID
    sender_id: uuid.UUID
    text: str
    timestamp: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True, json_encoders={uuid.UUID: str})


class MarkReadSchema(BaseModel):
    message_ids: List[uuid.UUID]
