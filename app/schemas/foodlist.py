from pydantic import BaseModel


class FoodListOut(BaseModel):
    id: int
    title: str
    kcal_100g: float
    amount: float


class FoodListAdd(BaseModel):
    id_food: int
    amount: float
