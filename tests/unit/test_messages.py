import pytest
import uuid
from unittest.mock import AsyncMock, Mock

from messages.services import MessageService


@pytest.mark.asyncio
async def test_create_message_calls_repo_and_commits(monkeypatch):
    fake_msg = Mock()
    fake_session = AsyncMock()

    async def fake_create_message(session, message):
        return fake_msg

    monkeypatch.setattr("messages.services.MessageRepository.create_message", fake_create_message)

    data = Mock(chat_id=uuid.uuid4(), text="Hello!", client_msg_id=uuid.uuid4())
    sender_id = uuid.uuid4()

    result = await MessageService.create_message(fake_session, data, sender_id)

    assert result == fake_msg
    fake_session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_get_chat_history_delegates(monkeypatch):
    fake_session = AsyncMock()
    fake_messages = [Mock(), Mock()]

    async def fake_get_by_chat(session, chat_id, limit, offset):
        return fake_messages

    monkeypatch.setattr("messages.services.MessageRepository.get_by_chat", fake_get_by_chat)

    result = await MessageService.get_chat_history(fake_session, uuid.uuid4(), 10, 0)

    assert result == fake_messages


@pytest.mark.asyncio
async def test_mark_as_read_commits(monkeypatch):
    fake_session = AsyncMock()
    fake_messages = [Mock()]

    async def fake_mark_as_read(session, ids, user_id):
        return fake_messages

    monkeypatch.setattr("messages.services.MessageRepository.mark_as_read", fake_mark_as_read)

    message_ids = [uuid.uuid4()]
    user_id = uuid.uuid4()

    result = await MessageService.mark_as_read(fake_session, message_ids, user_id)

    assert result == fake_messages
    fake_session.commit.assert_awaited()
