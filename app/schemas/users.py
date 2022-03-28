from pydantic import BaseModel, EmailStr
from typing import Optional

import datetime


# User register schema
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    gender: int
    age: int
    goal_weight: float
    height: float
    state: int
    is_nutr_adviser: bool


# User update in schema
class UserUpdate(BaseModel):
    goal_weight: Optional[float]
    height: Optional[float]
    state: Optional[int]
    is_nutr_adviser: Optional[bool]


# Response for user registration
class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime.datetime

    class Config:
        orm_mode = True


# Basic user endpoint response schema
class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    gender: int
    age: int
    state: int
    is_nutr_adviser: bool

    class Config:
        orm_mode = True


# User update response
class UserUpdatedOut(UserOut):
    goal_weight: float
    height: float


# Profile picture update
class ProfilePictureIn(BaseModel):
    profile_picture: bytes


# Login schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token response schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


# Token payload
class TokenData(BaseModel):
    id: Optional[str] = None
