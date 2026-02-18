import uuid

from fastapi import HTTPException
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from chats.models import Chat, ChatParticipant, ChatType, ParticipantRole


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
        await session.flush()
        await session.refresh(chat)
        return chat

    @staticmethod
    async def get_participant(
        session: AsyncSession, chat_id: uuid.UUID, user_id: uuid.UUID
    ) -> ChatParticipant:
        result = await session.execute(
            select(ChatParticipant).where(
                ChatParticipant.user_id == user_id, ChatParticipant.chat_id == chat_id
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_participants(
        session: AsyncSession, chat_id: uuid.UUID
    ) -> list[ChatParticipant]:
        result = await session.execute(
            select(ChatParticipant).where(ChatParticipant.chat_id == chat_id)
        )
        return result.scalars().all()

    @staticmethod
    async def add_participants(
        session: AsyncSession, participants: list[ChatParticipant]
    ):
        session.add_all(participants)
        await session.flush()

    @staticmethod
    async def remove_participant(
        session: AsyncSession, chat_id: uuid.UUID, user_id: uuid.UUID
    ):
        participant = await ChatRepository.get_participant(session, chat_id, user_id)
        if participant:
            await session.delete(participant)
            await session.flush()

    @staticmethod
    async def is_participant(
        session: AsyncSession, chat_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        result = await session.execute(
            select(ChatParticipant).where(
                ChatParticipant.user_id == user_id, ChatParticipant.chat_id == chat_id
            )
        )
        return result.scalars().first() is not None

    @staticmethod
    async def change_role(
        session: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        new_role: ParticipantRole,
    ):
        participant = await ChatRepository.get_participant(session, chat_id, user_id)
        participant.role = new_role
        await session.flush()

    @staticmethod
    async def find_personal_chat(
        session: AsyncSession, user1: uuid.UUID, user2: uuid.UUID
    ) -> Chat | None:
        result = await session.execute(
            select(Chat)
            .join(ChatParticipant)
            .where(
                Chat.type == ChatType.personal,
                ChatParticipant.user_id.in_([user1, user2]),
            )
            .group_by(Chat.id)
            .having(func.count(distinct(ChatParticipant.user_id)) == 2)
        )
        return result.scalars().first()
