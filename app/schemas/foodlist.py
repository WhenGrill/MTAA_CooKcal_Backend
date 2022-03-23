from pydantic import BaseModel


class FoodListOut(BaseModel):
    title: str
    kcal_100g: float
    amount: float


class FoodListAdd(BaseModel):
    id_food: int
    amount: float
