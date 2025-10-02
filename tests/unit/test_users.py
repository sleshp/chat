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
