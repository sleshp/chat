import uuid

from pydantic import BaseModel, EmailStr, Field


class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserReadSchema(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str