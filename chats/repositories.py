import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chats.models import Chat, ChatParticipant


class ChatRepository:
    @staticmethod
    async def get_user_chats(session: AsyncSession, user_id: uuid.UUID) -> list[Chat]:
        result = await session.execute(
            select(Chat).join(ChatParticipant).where(ChatParticipant.user_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, chat_id: uuid.UUID) -> Chat | None:
        return await session.get(Chat, chat_id)

    @staticmethod
    async def create(session: AsyncSession, chat: Chat):
        session.add(chat)
        await session.commit()
        await session.refresh(chat)
        return chat

    @staticmethod
    async def add_participants(session: AsyncSession, participants: list[ChatParticipant]):
        session.add_all(participants)
        await session.commit()

