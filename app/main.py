from fastapi import FastAPI
from .routers import food, foodlist, recipes, users, auth, weight_measurement
from .metadata import tags_metadata


app = FastAPI(openapi_tags=tags_metadata)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(food.router)
app.include_router(foodlist.router)
app.include_router(weight_measurement.router)
app.include_router(recipes.router)

# root for basic response (so not "not found" will be shown)
@app.get("/")
def root():
    return {"message": "MTAA - CooKcal Project"}
