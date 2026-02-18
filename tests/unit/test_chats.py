import uuid

import pytest
from fastapi import HTTPException

from chats.services import ChatService


@pytest.mark.asyncio
async def test_get_chat_not_found(mocker):
    fake_session = mocker.Mock()
    # репозиторий возвращает None
    mocker.patch("chats.services.ChatRepository.get_by_id", return_value=None)

    with pytest.raises(HTTPException) as e:
        await ChatService.get_chat(fake_session, uuid.uuid4())

    assert e.value.status_code == 404
    assert "Chat not found" in e.value.detail


@pytest.mark.asyncio
async def test_ensure_member_forbidden(mocker):
    fake_session = mocker.Mock()
    # репозиторий вернул False → пользователь не участник
    mocker.patch("chats.services.ChatRepository.is_participant", return_value=False)

    with pytest.raises(HTTPException) as e:
        await ChatService.ensure_member(fake_session, uuid.uuid4(), uuid.uuid4())

    assert e.value.status_code == 403
    assert "User not in chat" in e.value.detail


@pytest.mark.asyncio
async def test_create_chat_adds_creator_and_participants(mocker):
    fake_session = mocker.AsyncMock()

    fake_chat = mocker.Mock(id=uuid.uuid4())
    mocker.patch("chats.services.ChatRepository.create", return_value=fake_chat)
    mock_add = mocker.patch("chats.services.ChatRepository.add_participants")

    data = mocker.Mock(title="Test chat", type="group", participant_ids=[uuid.uuid4()])

    result = await ChatService.create_chat(fake_session, data, creator_id=uuid.uuid4())

    assert result == fake_chat
    mock_add.assert_awaited()
    fake_session.commit.assert_awaited()
