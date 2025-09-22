from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from users.schemas import UserReadSchema, UserCreateSchema, UserLoginSchema, TokenSchema

from users.services import UserService

user_router = APIRouter(prefix="/api/users", tags=["users"])


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@user_router.get("/", response_model=list[UserReadSchema])
async def get_users(session: AsyncSession = Depends(get_session)):
    return await UserService.list_users(session)


@user_router.post("/register", response_model=UserReadSchema)
async def register_user(user: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    return await UserService.register_user(session, user)


@user_router.get("/{user_id}", response_model=UserReadSchema)
async def get_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    user = await UserService.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.post("/login", response_model=TokenSchema)
async def login_user(response: Response, creds: UserLoginSchema, session: AsyncSession = Depends(get_session)):
    user = await UserService.get_user_by_email(session, creds.email)
    if user and UserService.verify_password(creds.password, user.password):
        access_token = UserService.create_access_token(data={"user_id": str(user.id)})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
