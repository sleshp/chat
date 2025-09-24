import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from messages.models import Messages
from messages.repositories import MessageRepository
from messages.schemas import MessageCreateSchema


class MessageService:
    @staticmethod
    async def create_message(session: AsyncSession, data: MessageCreateSchema, sender_id):
        message = Messages(chat_id=data.chat_id, sender_id=sender_id, text=data.text)
        return await MessageRepository.create_message(session, message)

    @staticmethod
    async def get_chat_history(session: AsyncSession, chat_id, limit: int, offset: int) ->list[Messages]:
        return await MessageRepository.get_by_chat(session, chat_id, limit, offset)

    @staticmethod
    async def mark_as_read(session: AsyncSession, message_id: uuid.UUID):
        return await MessageRepository.mark_as_read(session, message_id)