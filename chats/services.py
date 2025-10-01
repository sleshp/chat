import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from chats.models import Chat, ChatParticipant
from chats.repositories import ChatRepository
from chats.schemas import ChatCreateSchema


class ChatService:

    @staticmethod
    async def create_chat(session: AsyncSession, data: ChatCreateSchema, creator_id: uuid.UUID) -> Chat:
        chat = Chat(title=data.title, type=data.type)
        chat = await ChatRepository.create(session, chat)

        participants = [ChatParticipant(chat_id=chat.id, user_id=creator_id)]
        for uid in data.participant_ids:
            participants.append(ChatParticipant(chat_id=chat.id, user_id=uid))

        await ChatRepository.add_participants(session, participants)
        await session.commit()
        return chat

    @staticmethod
    async def get_chat(session: AsyncSession, chat_id: uuid.UUID) -> Chat:
        chat = await ChatRepository.get_by_id(session, chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    @staticmethod
    async def get_user_chats(session: AsyncSession, user_id: uuid.UUID) -> list[Chat]:
        return await ChatRepository.get_user_chats(session, user_id)

    @staticmethod
    async def ensure_member(session: AsyncSession, chat_id: uuid.UUID, user_id: uuid.UUID):
        if not await ChatRepository.is_participant(session, chat_id, user_id):
            raise HTTPException(status_code=403, detail="User not in chat")
