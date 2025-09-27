from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserSchema(BaseModel):
    id: str
    name: str
    age: int
    email: str
    address: str


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3)
    password: Optional[str] = None
    age: int = Field(..., gt=0)
    email: EmailStr
    address: str = Field(..., min_length=5)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    age: Optional[int] = Field(None, gt=0)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, min_length=5)
