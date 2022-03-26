from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from .. import models
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..database import get_db
from ..schemas.foodlist import FoodListOut, FoodListAdd

from datetime import datetime
from typing import List


router = APIRouter(
    prefix="/foodlist",
    tags=["Food List"]
)


@router.get("/", response_model=List[FoodListOut], status_code=status.HTTP_200_OK)
def get_food_list(date: str, curr_user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    food_list_query = db.query(models.Foodlist.id, models.Food.title, models.Food.kcal_100g, models.Foodlist.amount)\
        .join(models.Food).filter(and_(models.Foodlist.id_user == curr_user.id,
                                       and_(func.date(models.Foodlist.time) >= date),
                                       func.date(models.Foodlist.time) <= date))

    food_list = food_list_query.all()

    return food_list


@router.post("/", response_model=FoodListOut, status_code=status.HTTP_200_OK)
def add_food_to_food_list(new_food: FoodListAdd, curr_user: models.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    add_time = datetime.now()
    new_food_model = models.Foodlist(id_user=curr_user.id, time=add_time, **new_food.dict())
    db.add(new_food_model)
    db.commit()
    # db.refresh(new_food_model)

    fetched = db.query(models.Foodlist.id, models.Food.title, models.Food.kcal_100g, models.Foodlist.amount)\
        .join(models.Food).filter(and_(models.Foodlist.id_food == new_food.id_food,
                                       models.Foodlist.id_user == curr_user.id,
                                       models.Foodlist.time == add_time)).first()

    return fetched


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_from_food_list(id: int, curr_user: models.User = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    food_query = db.query(models.Foodlist).filter(models.Foodlist.id == id)
    food = food_query.first()

    if food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food listing not found")
    elif food.id_user != curr_user.id:
        raise ex_notAuthToPerformAction

    food_query.delete(synchronize_session=False)
    db.commit()
