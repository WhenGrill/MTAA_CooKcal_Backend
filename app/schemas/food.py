from pydantic import BaseModel


# Getting food based on ID
class FoodId(BaseModel):
    id: int


# Getting food based on Name
class FoodName(BaseModel):
    title: str


# Basic food response
class FoodOut(BaseModel):
    id: int
    title: str
    kcal_100g: float

    class Config:
        orm_mode = True
