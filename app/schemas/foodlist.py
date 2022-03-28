from pydantic import BaseModel


# Response foodlist schema
class FoodListOut(BaseModel):
    id: int
    title: str
    kcal_100g: float
    amount: float


# adding food list
class FoodListAdd(BaseModel):
    id_food: int
    amount: float
