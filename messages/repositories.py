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
    async def mark_as_read(session: AsyncSession, message_id: uuid.UUID) -> None:
        message = await session.get(Messages, message_id)
        if message:
            message.is_read = True
            await session.commit()
        else:
            raise HTTPException(status_code=404, detail="Message not found")
