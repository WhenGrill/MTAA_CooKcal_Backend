from pydantic import BaseModel

from typing import Union, ByteString, Optional
from .users import UserOut
import datetime


# Adding new recipe
class RecipeIn(BaseModel):
    title: str
    ingredients: str
    instructions: str
    kcal_100g: float


# Getting food based on ID
class RecipeOut(BaseModel):
    id: int
    title: str
    ingredients: str
    instructions: str
    kcal_100g: float
    creator: UserOut

    class Config:
        orm_mode = True


# Response recipe
class RecipePostOut(BaseModel):
    id: int
    id_user: int
    title: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


# Recipe update in
class RecipeUpdate(BaseModel):
    title: Optional[str]
    ingredients: Optional[str]
    instructions: Optional[str]
    kcal_100g: Optional[float]

