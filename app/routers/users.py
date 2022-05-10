from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status, WebSocket, WebSocketDisconnect
from starlette.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from PIL import Image

from ..database import get_db, ws_get_db
from .. import models, utils
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..schemas.users import UserOut, UserCreate, UserUpdate, UserUpdatedOut, UserCreateResponse
from ..utils import remove_none_from_dict, verify_image, ex_formatter

import io
import psycopg2
from psycopg2 import errors

# User router init
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

ex_userNotFound = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")


# GET endpoint for getting user based on name
@router.get("/", response_model=List[UserOut], status_code=status.HTTP_200_OK,
            responses={401: {'description': 'Unauthorized'}})
def get_users(name: Optional[str] = '', curr_user: models.User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    """
    **GET endpoint for getting user based on name**

    Query parameter:
    - Optional **name**: name of user, if not present, returns every user

    Response body:
    - **id**: id of user
    - **first_name**: first name of user
    - **last_name**: last name of user
    - **gender**: gender of user
    - **age**: age of user
    - **state**: state of user
    - **is_nutr_adviser**: boolean if he is nutritional adviser
    """

    # if no name was provided return all users
    if name == '':
        users = db.query(models.User).filter(models.User.id != 0).all()
    else:  # if name was provided fetch user by the name
        users = db.query(models.User).filter(func.lower(func.concat(
            models.User.first_name, ' ', models.User.last_name)).like(f"%{name.lower()}%"),
                                             models.User.id != 0).all()

    return users

@router.websocket("/ws")
async def ws_get_users(websocket: WebSocket):
    await websocket.accept()
    token: str = websocket.headers['authorization']
    db = ws_get_db()
    curr_user = get_current_user(token=token, db=db, is_wb=True)

    if not isinstance(curr_user, models.User):
       return curr_user

    try:
        while True:
            name: str = await websocket.receive_text()

            if name == '':
                users = db.query(models.User).filter(models.User.id != 0).all()
            else:  # if name was provided fetch user by the name
                users = db.query(models.User).filter(func.lower(func.concat(
                    models.User.first_name, ' ', models.User.last_name)).like(f"%{name.lower()}%"),
                                                     models.User.id != 0).all()
            l_users = []

            for x in users:
                new = UserOut(**x.__dict__)
                l_users.append(new.dict())

            await websocket.send_json({'status_code': 200, 'detail': l_users})
            db.close()

    except WebSocketDisconnect:
        pass


# GET endpoint for getting used based on id
@router.get("/{id}", response_model=UserUpdatedOut, status_code=status.HTTP_200_OK,
            responses={401: {'description': 'Unauthorized'},
                       404: {'description': 'Not found'}})
def get_one_user(id: int, curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # fetch user

    """
    **GET endpoint for getting used based on id**

    Query parameter:
    - **id**, id of user to fetch

    Response body:
    - **id**: id of user
    - **first_name**: first name of user
    - **last_name**: last name of user
    - **gender**: gender of user
    - **age**: age of user
    - **state**: state of user
    - **is_nutr_adviser**: boolean if he is nutritional adviser
    - **email**: email of user
    - **goal_weight**: goal weight of user
    - **height**: height of user

    """

    user = db.query(models.User).filter(models.User.id == id).first()

    if user is None or id == 0:     # if user does not exists or it is anonymous user
        raise ex_userNotFound

    return user


# GET endpoint for getting users's image
@router.get("/{id}/image", status_code=status.HTTP_200_OK,
            responses={204: {'description': 'No content'},
                       401: {'description': 'Unauthorized'},
                       404: {'description': 'Not found'}})
def get_user_profile_picture(id: int, curr_user: models.User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """
    **GET endpoint for getting users's profile picture**

    Query parameter:
    - **id**: id of user

    Response body:
    - **User's profile picture**

    """

    user = db.query(models.User.profile_picture).filter(models.User.id == id).first()

    if user is None or id == 0:     # if user does not exist
        raise ex_userNotFound
    elif user.profile_picture is None:      # if user does not have a profile picture
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    im = Image.open(io.BytesIO(user.profile_picture))   # display image
    return StreamingResponse(io.BytesIO(user.profile_picture), media_type=f"image/{im.format.lower()}")


# POST endpoint for registering a new user
@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED,
             responses={400: {'description': 'Bad request - email taken'},
                        403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'}})
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # hash the user's password

    """
    **POST endpoint for registering a new user**

    Request body:
    - **email**: user's email
    - **password**: user's password
    - **first_name**: user's name
    - **last_name**: user's lastname
    - **gender**: user's gender
    - **age**: user's age
    - **goal_weight**: user's weight
    - **height**: user's height
    - **state**: user's state
    - **is_nutr_adviser**: boolean if user is_nutr_adviser

    Response body:
    - **id**: id of user
    - **first_name**: first name of user
    - **last_name**: last name of user
    - **gender**: gender of user
    - **age**: age of user
    - **state**: state of user
    - **is_nutr_adviser**: boolean if he is nutritional adviser
    - **created_at**: time of user creation

    """

    hashed_password = utils.pwd_hash(user_data.password)
    user_data.password = hashed_password

    user_reg_data = models.User(**user_data.dict())
    try:    # add user do database
        db.add(user_reg_data)
        db.commit()
    except IntegrityError as e:     # if constrains were violated
        if isinstance(e.orig, psycopg2.errors.lookup("23505")):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"E-mail '{user_reg_data.email}' already registered.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:  # if other exception occured (data error)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    return db.query(models.User).filter(models.User.email == user_reg_data.email).first()


# PUT endpoint for updating users information
@router.put("/{id}", response_model=UserUpdatedOut, status_code=status.HTTP_200_OK,
            responses={304: {'description': 'Not modified'},
                       401: {'description': 'Unauthorized'},
                       403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'}})
def update_user_data(id: int, updated_user: UserUpdate, db: Session = Depends(get_db),
                     curr_user: models.User = Depends(get_current_user)):
    """
    **PUT endpoint for updating users information**

    Request body:
    - Optional **goal_weight**: user's weight
    - Optional **height**: user's height
    - Optional **state**: user's state
    - Optional **is_nutr_adviser**: boolean if user is_nutr_adviser

    Response body:
    - **id**: id of user
    - **first_name**: first name of user
    - **last_name**: last name of user
    - **gender**: gender of user
    - **age**: age of user
    - **state**: state of user
    - **is_nutr_adviser**: boolean if he is nutritional adviser
    - **email**: user's email
    - **goal_weight**: user's weight
    - **height**: user's height

    """

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None or id == 0:     # if user does not exist
        raise ex_userNotFound
    elif user.id != curr_user.id:   # if current user does not match the fetched user
        raise ex_notAuthToPerformAction
    elif all(value is None for value in updated_user.dict().values()):  # if there are no things to update (empty json)
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Nothing to update")

    try:    # update user
        user_query.update(remove_none_from_dict(updated_user.dict()), synchronize_session=False)
        db.commit()
    except IntegrityError as e:     # if constrains in database were violated
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:      # if other exception occured (data error)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    return user_query.first()


# PUT endpoint for updating user's image
@router.put("/{id}/image", status_code=status.HTTP_200_OK,
            responses={401: {'description': 'Unauthorized'},
                       404: {'description': 'Not found'},
                       413: {'description': 'Request entity too large (exceeded 2.7MB)'},
                       415: {'description': 'Unsupported media type'}})
def update_user_profile_picture(id: int, prof_picture: UploadFile = File(...),
                                curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    **PUT endpoint for updating user's profile picture**

    Query parameter:
    - **id**: id of user

    Request body:
    - **User profile picture**

    Response body:
    - **User profile picture**

    """

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None or id == 0:     # if user does not exist
        raise ex_userNotFound
    elif user.id != curr_user.id:   # if fetched id does not match current user
        raise ex_notAuthToPerformAction

    verified_image = verify_image(prof_picture.file.read())     # verifycation if file is a valid picture file

    user_query.update({'profile_picture': verified_image}, synchronize_session=False)
    db.commit()

    return StreamingResponse(io.BytesIO(user_query.first().profile_picture),
                             media_type=prof_picture.content_type)


# DELETE endpoint for deleting user
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT,
               responses={401: {'description': 'Unauthorized'},
                          404: {'description': 'Not found'}})
def delete_user_account(id: int, curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    """
    **DELETE endpoint for user**

    Query parameter:
    - **id**: id of user

    """

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user is None or id == 0:  # if user does not exist raise an exception
        raise ex_userNotFound
    elif user.id != curr_user.id:   # if current user is not the fecthed user raise an exception
        raise ex_notAuthToPerformAction

    user_query.delete(synchronize_session=False)    # delete user
    db.commit()
