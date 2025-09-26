import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user, get_session
from messages.schemas import MessageReadSchema, MessageCreateSchema, MarkReadSchema
from messages.services import MessageService
from users.models import User

messages_router = APIRouter(prefix='/api/messages', tags=['messages'])


@messages_router.post('/', response_model=MessageReadSchema)
async def send_message(data: MessageCreateSchema, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await MessageService.create_message(data=data, sender_id=current_user.id, session=session)


@messages_router.get('/{chat_id}', response_model=list[MessageReadSchema])
async def get_chat_history(chat_id: uuid.UUID, session: AsyncSession = Depends(get_session), limit: int = 50, offset: int = 0):
    return await MessageService.get_chat_history(chat_id=chat_id, session=session, limit=limit, offset=offset)


@messages_router.patch('/{message_id}/read')
async def mark_as_read(data: MarkReadSchema, session: AsyncSession = Depends(get_session)):
    messages = await MessageService.mark_as_read(message_ids=data.message_ids, session=session)
    return {"updated": [str(m.id) for m in messages]}
