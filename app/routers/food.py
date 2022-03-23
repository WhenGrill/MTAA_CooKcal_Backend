from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..database import get_db
from .. import models
from ..schemas import food

router = APIRouter(
    prefix="/food",
    tags=["Food"]
)


@router.get("/", response_model=List[food.FoodOut])
def root(title: Optional[str] = '', db: Session = Depends(get_db)):
    if title != '':
        answer = db.query(models.Food).filter(func.lower(models.Food.title).like(f"%{title}%")).all()
    else:
        answer = db.query(models.Food).all()

    return answer


@router.get("/{food_id}", response_model=food.FoodOut)
def root(food_id: int, db: Session = Depends(get_db)):
    answer = db.query(models.Food).filter(models.Food.id == food_id).first()

    return answer

