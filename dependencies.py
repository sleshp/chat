from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from users.services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_session() -> AsyncSession:

    async with async_session() as session:
        yield session


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return await UserService.get_current_user_by_token(session, token)
