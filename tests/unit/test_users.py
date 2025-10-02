from unittest.mock import AsyncMock, Mock

import pytest
from users.services import UserService


def test_hash_and_verify_password():
    password = "secret123"
    hashed = UserService.hash_password(password)

    assert hashed != password
    assert UserService.verify_password(password, hashed) is True
    assert UserService.verify_password("wrong", hashed) is False


def test_create_access_token_returns_jwt():
    token = UserService.create_access_token({"sub": "user123"})
    assert isinstance(token, str)
    assert len(token) > 20


@pytest.mark.asyncio
async def test_register_user_calls_repo(monkeypatch):
    fake_user = Mock(email="alice@example.com")
    async def fake_create(session, user): return fake_user

    monkeypatch.setattr("users.services.UserRepository.create", fake_create)

    fake_session = AsyncMock()
    user_in = Mock(name="Alice", email="alice@example.com", password="secret")

    result = await UserService.register_user(fake_session, user_in)
    assert result.email == "alice@example.com"