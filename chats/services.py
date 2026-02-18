import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from chats.models import Chat, ChatParticipant, ChatType, ParticipantRole
from chats.repositories import ChatRepository
from chats.schemas import ChatCreateSchema


class ChatService:

    @staticmethod
    async def create_chat(
        session: AsyncSession, data: ChatCreateSchema, creator_id: uuid.UUID
    ) -> Chat:
        chat_type = data.type
        if chat_type == ChatType.personal:
            if len(data.participant_ids) != 1:
                raise HTTPException(
                    status_code=400,
                    detail="Personal chat requires exactly one participant",
                )
            other_id = data.participant_ids[0]
            if other_id == creator_id:
                raise HTTPException(
                    status_code=400, detail="Cannot create personal chat with yourself"
                )

            existing = await ChatRepository.find_personal_chat(
                session, creator_id, other_id
            )
            if existing:
                return existing

        chat = Chat(title=data.title, type=chat_type)
        chat = await ChatRepository.create(session, chat)

        if chat.type == ChatType.group:
            participants: list[ChatParticipant] = [
                ChatParticipant(
                    chat_id=chat.id, user_id=creator_id, role=ParticipantRole.owner
                )
            ]
            for uid in data.participant_ids:
                participants.append(
                    ChatParticipant(
                        chat_id=chat.id, user_id=uid, role=ParticipantRole.member
                    )
                )
        else:
            participants = [
                ChatParticipant(
                    chat_id=chat.id, user_id=creator_id, role=ParticipantRole.member
                ),
                ChatParticipant(
                    chat_id=chat.id,
                    user_id=data.participant_ids[0],
                    role=ParticipantRole.member,
                ),
            ]

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
    async def ensure_member(
        session: AsyncSession, chat_id: uuid.UUID, user_id: uuid.UUID
    ):
        if not await ChatRepository.is_participant(session, chat_id, user_id):
            raise HTTPException(status_code=403, detail="User not in chat")

    @staticmethod
    async def get_participants(session: AsyncSession, chat_id: uuid.UUID):
        participants = await ChatRepository.get_participants(session, chat_id)
        if not participants:
            raise HTTPException(404, "Chat not found or empty")
        return participants

    @staticmethod
    async def change_role(
        session: AsyncSession,
        chat_id: uuid.UUID,
        requester_id: uuid.UUID,
        user_id: uuid.UUID,
        new_role: ParticipantRole,
    ):
        chat = await ChatRepository.get_by_id(session, chat_id)
        if not chat:
            raise HTTPException(404, "Chat not found")

        if new_role == ParticipantRole.owner:
            raise HTTPException(status_code=403, detail="You cant give owner role")

        requester = await ChatRepository.get_participant(session, chat_id, requester_id)
        user = await ChatRepository.get_participant(session, chat_id, user_id)
        if requester is None or user is None:
            raise HTTPException(status_code=403, detail="User not in chat")
        if requester.role == ParticipantRole.member:
            raise HTTPException(status_code=403, detail="Not allowed to change role")
        await ChatRepository.change_role(session, chat_id, user_id, new_role)
        await session.commit()

    @staticmethod
    async def add_member(
        session: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        requester_id: uuid.UUID,
    ) -> ChatParticipant:
        requester = await ChatRepository.get_participant(session, chat_id, requester_id)
        if requester is None:
            raise HTTPException(403, "You are not in this chat")
        if requester.role == ParticipantRole.member:
            raise HTTPException(403, "Not allowed to add members")
        existing = await ChatRepository.get_participant(session, chat_id, user_id)
        if existing:
            raise HTTPException(status_code=409, detail="User already in chat")
        new_member = [
            ChatParticipant(
                chat_id=chat_id, user_id=user_id, role=ParticipantRole.member
            )
        ]
        await ChatRepository.add_participants(session, new_member)
        await session.commit()
        return new_member[0]

    @staticmethod
    async def remove_member(
        session: AsyncSession,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
        requester_id: uuid.UUID,
    ) -> ChatParticipant:
        requester = await ChatRepository.get_participant(session, chat_id, requester_id)
        existing = await ChatRepository.get_participant(session, chat_id, user_id)
        if requester is None or existing is None:
            raise HTTPException(404, "User not found in chat")
        if requester.role == ParticipantRole.member:
            raise HTTPException(403, "Not allowed to remove members")
        if (
            requester.role == ParticipantRole.admin
            and existing.role != ParticipantRole.member
        ):
            raise HTTPException(403, "Admin can remove only members")
        await ChatRepository.remove_participant(session, chat_id, user_id)
        await session.commit()

    @staticmethod
    async def leave_chat(session: AsyncSession, chat_id: uuid.UUID, user_id: uuid.UUID):
        participant = await ChatRepository.get_participant(session, chat_id, user_id)
        if not participant:
            raise HTTPException(status_code=404, detail="You are not in this chat")
        await ChatRepository.remove_participant(session, chat_id, user_id)
        await session.commit()
