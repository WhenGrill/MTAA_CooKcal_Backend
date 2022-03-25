from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..database import get_db
from .. import models, utils
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..schemas.users import UserOut, UserCreate, UserUpdate, UserUpdatedOut, UserCreateResponse, ProfilePictureIn
from ..utils import remove_none_from_dict

import io
import psycopg2
from psycopg2 import errors


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

ex_userNotFound = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")


@router.get("/", response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_users(name: Optional[str] = '', curr_user: models.User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    if name == '':
        users = db.query(models.User).all()
    else:
        users = db.query(models.User).filter(func.lower(
            func.concat(models.User.first_name, ' ', models.User.last_name)).like(f"%{name.lower()}%")).all()

    return users


@router.get("/{id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_one_user(id: int, curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise ex_userNotFound

    return user


@router.get("/{id}/image", status_code=status.HTTP_200_OK)
def get_user_profile_picture(id: int, curr_user: models.User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    user = db.query(models.User.profile_picture).filter(models.User.id == id).first()

    if user.profile_picture is None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    return StreamingResponse(io.BytesIO(user.profile_picture.tobytes()), media_type="image/png")


@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.pwd_hash(user_data.password)
    user_data.password = hashed_password

    user_reg_data = models.User(**user_data.dict())
    try:
        db.add(user_reg_data)
        db.commit()
    except IntegrityError as e:
        if isinstance(e.orig, psycopg2.errors.lookup("23505")):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"E-mail '{user_reg_data.email}' already taken")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return db.query(models.User).filter(models.User.email == user_reg_data.email).first()


@router.put("/{id}", response_model=UserUpdatedOut, status_code=status.HTTP_200_OK)
def update_user_data(id: int, updated_user: UserUpdate, db: Session = Depends(get_db),
                     curr_user: models.User = Depends(get_current_user)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None:
        raise ex_userNotFound
    elif user.id != curr_user.id:
        raise ex_notAuthToPerformAction

    user_query.update(remove_none_from_dict(updated_user.dict()), synchronize_session=False)
    db.commit()

    return user_query.first()


@router.put("/{id}/image", status_code=status.HTTP_200_OK)
def update_user_profile_picture(id: int, updated_profile_picture: ProfilePictureIn,
                                curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None:
        raise ex_userNotFound
    elif user.id != curr_user.id:
        raise ex_notAuthToPerformAction

    user_query.update(remove_none_from_dict(updated_profile_picture.dict()), synchronize_session=False)
    db.commit()

    return StreamingResponse(io.BytesIO(user_query.first().profile_picture.tobytes()), media_type="image/png")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None:
        raise ex_userNotFound
    elif user.id != curr_user.id:
        raise ex_notAuthToPerformAction

    user_query.delete(synchronize_session=False)
    db.commit()
