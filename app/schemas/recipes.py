from pydantic import BaseModel

from typing import Union, ByteString, Optional
from .users import UserOut
import datetime


class RecipeIn(BaseModel):
    title: str
    ingredients: str
    instructions: str
    kcal_100g: float


# Getting food based on ID
class RecipeOut(BaseModel):
    id: int
    # id_user: int
    title: str
    ingredients: str
    instructions: str
    kcal_100g: float
    creator: UserOut

    class Config:
        orm_mode = True


class RecipePostOut(BaseModel):
    id: int
    id_user: int
    title: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class RecipeOutPicture(BaseModel):
    recipe_picture: bytes = None

    class Config:
        orm_mode = True


class RecipeUpdate(BaseModel):
    title: Optional[str]
    ingredients: Optional[str]
    instructions: Optional[str]
    kcal_100g: Optional[float]


class RecipeInPicture(BaseModel):
    recipe_picture: bytes
