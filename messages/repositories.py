import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from messages.models import Messages


class MessageRepository:

    @staticmethod
    async def create_message(session: AsyncSession, message: Messages) -> Messages:
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    @staticmethod
    async def get_by_chat(session: AsyncSession, chat_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[Messages]:
        result = await session.execute(
            select(Messages).where(Messages.chat_id == chat_id).order_by(Messages.timestamp.asc()).limit(limit).offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_client_id(session: AsyncSession, client_msg_id: uuid.UUID) -> Messages:
        result = await session.execute(
            select(Messages).where(Messages.client_msg_id == client_msg_id)
        )
        return result.scalars().first()

    @staticmethod
    async def mark_as_read(session: AsyncSession, message_ids: list[uuid.UUID]) -> list[Messages]:
        result = []
        for mid in message_ids:
            message = await session.get(Messages, mid)
            if message:
                message.is_read = True
                result.append(message)
        await session.commit()
        return result
