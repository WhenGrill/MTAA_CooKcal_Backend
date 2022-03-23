from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from .. import models, utils
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..schemas.users import UserOut, UserCreate, ProfilePictureIn

import io


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


@router.get("/{id}", response_model=UserOut)
def get_one_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    return user


@router.get("/{id}/image")
def get_user_profile_picture(id: int, curr_user: models.User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    user = db.query(models.User, models.User.profile_picture).filter(models.User.id == id).first()

    return StreamingResponse(io.BytesIO(user.profile_picture.tobytes()), media_type="image/png")


@router.post("/", response_model=UserOut)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.pwd_hash(user_data.password)
    user_data.password = hashed_password

    user_reg_data = models.User(**user_data.dict())
    db.add(user_reg_data)
    db.commit()
    db.refresh(user_reg_data)

    return user_reg_data


@router.put("/{id}", response_model=UserOut)
def update_user_data(id: int, updated_user: UserCreate, db: Session = Depends(get_db),
                     curr_user: models.User = Depends(get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} was not found")
    elif user.id != curr_user.id:
        raise ex_notAuthToPerformAction

    user_query.update(updated_user.dict(), synchronize_session=False)
    db.commit()

    return user_query.first()


@router.put("/{id}/image")
def update_user_profile_picture(id: int, updated_profile_picture: ProfilePictureIn,
                                curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} was not found")
    elif user.id != curr_user.id:
        raise ex_notAuthToPerformAction

    user_query.update(updated_profile_picture.dict(), synchronize_session=False)
    db.commit()

    return StreamingResponse(io.BytesIO(user_query.first().profile_picture.tobytes()), media_type="image/png")


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
