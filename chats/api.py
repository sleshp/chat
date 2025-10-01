import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chats.models import Chat
from chats.schemas import ChatReadSchema, ChatCreateSchema
from chats.services import ChatService
from dependencies import get_current_user, get_session
from users.models import User

chat_router = APIRouter(prefix="/api/chats", tags=["chat"])


@chat_router.post("/", response_model=ChatReadSchema)
async def create_chat(data: ChatCreateSchema, current_user: User = Depends(get_current_user), session: AsyncSession=Depends(get_session)):
    return await ChatService.create_chat(session, data, current_user.id)


@chat_router.get("/my", response_model=list[ChatReadSchema])
async def get_my_chat(current_user: User = Depends(get_current_user), session: AsyncSession=Depends(get_session)):

    return await ChatService.get_user_chats(session, current_user.id)


@chat_router.get("/{chat_id}", response_model=ChatReadSchema)
async def get_chat(
        chat_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession=Depends(get_session)
):
    await ChatService.ensure_member(session, chat_id, current_user.id)
    return await ChatService.get_chat(session, chat_id)
