import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User


class UserRepository:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(select(User))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: uuid.UUID):
        return await session.get(User, user_id)

    @staticmethod
    async def get_by_email(session: AsyncSession, email: str):
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, user: User):
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
