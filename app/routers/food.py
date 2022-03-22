from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..schemas import food
from typing import List, Optional

router = APIRouter(
    prefix="/food",
    tags=["Food"]
)


@router.get("/", response_model=List[food.FoodOut])
def root(title: Optional[str] = '', db: Session = Depends(get_db)):
    if title != '':
        answer = db.query(models.Food).filter(models.Food.title == title).all()
    else:
        answer = db.query(models.Food).all()

    return answer


@router.get("/{food_id}", response_model=food.FoodOut)
def root(food_id: int, db: Session = Depends(get_db)):
    answer = db.query(models.Food).filter(models.Food.id == food_id).first()

    return answer

