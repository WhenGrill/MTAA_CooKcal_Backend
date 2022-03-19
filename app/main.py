from fastapi import FastAPI
from .routers import food, foodlist, recipes, users

app = FastAPI()

# Routers
app.include_router(food.router)
app.include_router(foodlist.router)
app.include_router(recipes.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "MTAA - CooKcal Project"}
