from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from typing import List


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[schemas.UserOut])
def root(db: Session = Depends(get_db)):
    answer = db.query(models.User).all()

    return answer
