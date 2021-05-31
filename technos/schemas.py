from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    email: str
    password: str
    username: str


class UserCreate(UserBase):
    email: str
    username: str
    password: str


class User(UserBase):
    password: str
    email: str
    username: str

    class Config:
        orm_mode: True


class TokenData(BaseModel):
    username: Optional[str] = None
