from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from .. import models, utils
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..schemas.users import UserOut, UserCreate


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[UserOut])
def get_users(name: Optional[str] = '', db: Session = Depends(get_db)):
    if name == '':
        users = db.query(models.User).all()
    else:
        users = db.query(models.User).filter(func.lower(
            func.concat(models.User.first_name, ' ', models.User.last_name)).like(f"%{name}%")).all()

    return users


@router.post("/", response_model=UserOut)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.pwd_hash(user_data.password)
    user_data.password = hashed_password

    user_reg_data = models.User(**user_data.dict())
    db.add(user_reg_data)
    db.commit()
    db.refresh(user_reg_data)

    return user_reg_data


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} was not found")
    elif user.id != curr_user.id:
        raise ex_notAuthToPerformAction

    user_query.delete(synchronize_session=False)
    db.commit()
