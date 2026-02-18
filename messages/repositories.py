import uuid

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from chats.models import ChatParticipant
from messages.models import Messages


class MessageRepository:

    @staticmethod
    async def create_message(session: AsyncSession, message: Messages) -> Messages:
        stmt = (
            insert(Messages)
            .values(
                id=message.id,
                chat_id=message.chat_id,
                sender_id=message.sender_id,
                text=message.text,
                client_msg_id=message.client_msg_id,
            )
            .on_conflict_do_nothing(index_elements=["client_msg_id"])
            .returning(Messages)
        )
        result = await session.execute(stmt)
        row = result.fetchone()
        if row:
            return row[0]
        else:
            return await MessageRepository.get_by_client_id(
                session, message.client_msg_id
            )

    @staticmethod
    async def get_by_chat(
        session: AsyncSession, chat_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[Messages]:
        result = await session.execute(
            select(Messages)
            .where(Messages.chat_id == chat_id)
            .order_by(Messages.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_client_id(
        session: AsyncSession, client_msg_id: uuid.UUID
    ) -> Messages:
        result = await session.execute(
            select(Messages).where(Messages.client_msg_id == client_msg_id)
        )
        return result.scalars().first()

    @staticmethod
    async def mark_as_read(
        session: AsyncSession, message_ids: list[uuid.UUID], user_id: uuid.UUID
    ) -> list[Messages]:
        if not message_ids:
            return []

        allowed_ids_subq = (
            select(Messages.id)
            .join(ChatParticipant, ChatParticipant.chat_id == Messages.chat_id)
            .where(
                ChatParticipant.user_id == user_id,
                Messages.id.in_(message_ids),
            )
            .subquery()
        )

        stmt = (
            update(Messages)
            .where(Messages.id.in_(select(allowed_ids_subq.c.id)))
            .values(
                is_read=True,
            )
            .returning(Messages)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())
