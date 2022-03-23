from fastapi import APIRouter, Depends
from sqlalchemy import func, and_, Date
from sqlalchemy.orm import Session

from .. import models
from ..oauth2 import get_current_user
from ..database import get_db
from ..schemas.foodlist import FoodListOut

from typing import List


router = APIRouter(
    prefix="/foodlist",
    tags=["Food List"]
)


@router.get("/", response_model=List[FoodListOut])
def get_food_list(date: str, curr_user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    food_list_query = db.query(models.Food.title, models.Food.kcal_100g, models.Foodlist.amount)\
        .join(models.Food).filter(and_(models.Foodlist.id_user == curr_user.id,
                                       and_(func.date(models.Foodlist.time) >= date),
                                       func.date(models.Foodlist.time) <= date))

    food_list = food_list_query.all()

    return food_list
