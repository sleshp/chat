import uuid
from datetime import timedelta, datetime, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_auth_data
from users.models import User
from users.repositories import UserRepository
from users.schemas import UserCreateSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=30)
        to_encode.update({"exp": expire})
        auth_data = get_auth_data()
        encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
        return encode_jwt

    @staticmethod
    async def register_user(session: AsyncSession, user: UserCreateSchema):
        data = user.model_dump()
        data["password"] = UserService.hash_password(data["password"])
        new_user = User(**data)
        return await UserRepository.create(session, new_user)

    @staticmethod
    async def list_users(session: AsyncSession):
        return await UserRepository.get_all(session)

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID):
        return await UserRepository.get_by_id(session, user_id)

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str):
        return await UserRepository.get_by_email(session, email)