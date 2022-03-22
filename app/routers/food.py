from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..schemas import food
from typing import List

router = APIRouter(
    prefix="/food",
    tags=["Food"]
)


@router.get("/", response_model=List[food.FoodOut])
def root(db: Session = Depends(get_db)):
    answer = db.query(models.Food).all()

    return answer
