from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, utils, schemas
from ..schemas.users import UserOut, UserCreate


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    answer = db.query(models.User).all()

    return answer


@router.post("/", response_model=UserOut)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.pwd_hash(user_data.password)
    user_data.password = hashed_password

    user_reg_data = models.User(**user_data.dict())
    db.add(user_reg_data)
    db.commit()
    db.refresh(user_reg_data)

    return user_reg_data
