from pydantic import BaseModel, EmailStr
from typing import Optional


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


class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):  # Token payload
    id: Optional[str] = None
