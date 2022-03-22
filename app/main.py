from fastapi import FastAPI, Depends
from .routers import food, foodlist, recipes, users, auth

from .database import get_db


app = FastAPI()

# Routers
app.include_router(auth.router)
app.include_router(food.router)
app.include_router(foodlist.router)
app.include_router(recipes.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "MTAA - CooKcal Project"}
