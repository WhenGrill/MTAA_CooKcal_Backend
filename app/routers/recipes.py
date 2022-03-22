from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..schemas import recipes
from typing import List, Optional

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


@router.get("/", response_model=List[recipes.RecipeOut])
def root(title: Optional[str] = '', db: Session = Depends(get_db)):
    if title != '':
        answer = db.query(models.Recipe).filter(models.Recipe.title == title).all()
    else:
        answer = db.query(models.Recipe).all()

    return answer