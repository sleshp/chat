import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chats.services import ChatService
from dependencies import get_current_user, get_session
from messages.schemas import MarkReadSchema, MessageCreateSchema, MessageReadSchema
from messages.services import MessageService
from users.models import User

messages_router = APIRouter(prefix="/api/messages", tags=["messages"])


@messages_router.post("/", response_model=MessageReadSchema)
async def send_message(
    data: MessageCreateSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await ChatService.ensure_member(session, data.chat_id, current_user.id)
    return await MessageService.create_message(
        data=data, sender_id=current_user.id, session=session
    )


@messages_router.get("/{chat_id}", response_model=list[MessageReadSchema])
async def get_chat_history(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    limit: int = 50,
    offset: int = 0,
):
    await ChatService.ensure_member(session, chat_id, current_user.id)
    return await MessageService.get_chat_history(
        chat_id=chat_id, session=session, limit=limit, offset=offset
    )


@messages_router.patch("/read")
async def mark_as_read(
    data: MarkReadSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    messages = await MessageService.mark_as_read(
        message_ids=data.message_ids, session=session, user_id=current_user.id
    )
    return {"updated": [str(m.id) for m in messages]}
