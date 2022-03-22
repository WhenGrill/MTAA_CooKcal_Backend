from pydantic import BaseModel


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


