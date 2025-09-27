from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from .user_schema import UserSchema


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthSchema(BaseModel):
    user: UserSchema
    token: Token


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=5)
