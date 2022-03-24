from pydantic import BaseModel

from typing import Union, ByteString


class RecipeIn(BaseModel):
    title: str
    ingredients: str
    instructions: str
    kcal_100g: float


# Getting food based on ID
class RecipeOut(BaseModel):
    id: int
    user_id: int
    title: str
    ingredients: str
    instructions: str
    kcal_100g: float

    class Config:
        orm_mode = True


class RecipeOutPicture(BaseModel):
    recipe_picture: bytes = None

    class Config:
        orm_mode = True
