from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user, get_session
from users.schemas import UserReadSchema, UserCreateSchema, TokenSchema

from users.services import UserService

user_router = APIRouter(prefix="/api/users", tags=["users"])



@user_router.get("/", response_model=list[UserReadSchema])
async def get_users(session: AsyncSession = Depends(get_session)):
    return await UserService.list_users(session)


@user_router.post("/register", response_model=UserReadSchema)
async def register_user(user: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    return await UserService.register_user(session, user)


@user_router.post("/login", response_model=TokenSchema)
async def login_user(response: Response, creds: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await UserService.get_user_by_email(session, creds.username)
    if user and UserService.verify_password(creds.password, user.password):
        access_token = UserService.create_access_token(data={"sub": str(user.id)})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect email or password")


@user_router.get("/me", response_model=UserReadSchema)
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user


@user_router.get("/{user_id}", response_model=UserReadSchema)
async def get_user_by_id(user_id: UUID, session: AsyncSession = Depends(get_session)):
    user = await UserService.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
