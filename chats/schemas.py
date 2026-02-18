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
    created_at: Optional[str]

    class Config:
        from_attributes = True


class ParticipantRoleSchema(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class ChatParticipantBase(BaseModel):
    user_id: uuid.UUID
    role: ParticipantRoleSchema

    class Config:
        from_attributes = True


class ChatParticipantReadSchema(ChatParticipantBase):
    id: uuid.UUID


class ChatParticipantListSchema(BaseModel):
    chat_id: uuid.UUID
    participants: List[ChatParticipantReadSchema]


class ChatDetailSchema(ChatReadSchema):
    participants: List[ChatParticipantReadSchema] = []

    class Config:
        from_attributes = True


class DetailResponseSchema(BaseModel):
    detail: str
