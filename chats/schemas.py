import uuid
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class ChatTypeSchema(str, Enum):
    personal = "personal"
    group = "group"


class ChatCreateSchema(BaseModel):
    title: Optional[str] = None
    type: ChatTypeSchema
    participant_ids: List[uuid.UUID]


class ChatReadSchema(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    type: ChatTypeSchema

    class Config:
        from_attributes = True
