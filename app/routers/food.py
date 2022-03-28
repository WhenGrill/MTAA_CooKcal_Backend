from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..database import get_db
from .. import models
from ..oauth2 import get_current_user
from ..schemas import food

router = APIRouter(
    prefix="/food",
    tags=["Food"],
    responses={401: {'description': 'Unauthorized'}}
)


@router.get("/", response_model=List[food.FoodOut], status_code=status.HTTP_200_OK)
def get_all_food_or_by_name(title: Optional[str] = '', curr_user: models.User = Depends(get_current_user),
                            db: Session = Depends(get_db)):
    if title != '':
        title = title.lower()
        answer = db.query(models.Food).filter(func.lower(models.Food.title).like(f"%{title}%")).all()
    else:
        answer = db.query(models.Food).all()

    return answer


@router.get("/{id}", response_model=food.FoodOut, status_code=status.HTTP_200_OK,
            responses={404: {'description': 'Not found'}})
def get_food_by_id(id: int, curr_user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    answer = db.query(models.Food).filter(models.Food.id == id).first()
    if answer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    return answer

