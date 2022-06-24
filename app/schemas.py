from typing import Optional
from pydantic import BaseModel, EmailStr, Field, conint
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    published: bool=True


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass


class User(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: User

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token = str
    token_type = str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1, ge=0)
