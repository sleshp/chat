from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from database import async_session
from users.services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_session() -> AsyncSession:

    async with async_session() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    return await UserService.get_current_user_by_token(session, token)
