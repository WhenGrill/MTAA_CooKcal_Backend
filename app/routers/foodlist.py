from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import models
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..database import get_db
from ..schemas.foodlist import FoodListOut, FoodListAdd
from ..utils import ex_formatter

from datetime import datetime
from dateutil import parser
from typing import List

# Food list router init
router = APIRouter(
    prefix="/foodlist",
    tags=["Food List"],
    responses={401: {'description': 'Unauthorized'}}
)


# GET endpoint for getting food list based on date
@router.get("/", response_model=List[FoodListOut], status_code=status.HTTP_200_OK)
def get_food_list(date: str, curr_user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    """
    **GET endpoint for getting food list based on date**

    Query parameter:
    - Optional **date**: date of addition of food to foodlist, if empty fetches every food of current user

    Response body:
    - **id**: id of food in foodlist
    - **title**: title of added food
    - **kcal_100g**: amount of kcal for 100g
    - **amount**: amount of added food

    """

    # test if input is date
    try:
        test_date = str(parser.parse(date).date())
    except Exception:
        return []

    # fetch the list
    food_list_query = db.query(models.Foodlist.id, models.Food.title, models.Food.kcal_100g, models.Foodlist.amount) \
        .join(models.Food).filter(and_(models.Foodlist.id_user == curr_user.id,
                                       and_(func.date(models.Foodlist.time) >= test_date),
                                       func.date(models.Foodlist.time) <= test_date))

    food_list = food_list_query.all()

    return food_list


# POST endpoint for adding new food to foodlist
@router.post("/", response_model=FoodListOut, status_code=status.HTTP_200_OK,
             responses={403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'},
                        404: {'description': 'Not found'}})
def add_food_to_food_list(new_food: FoodListAdd, curr_user: models.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    """
    **POST endpoint for adding new food to foodlist**

    Request body:
    - **id_food**: id of chosen food
    - **amount**: amount of chosen food

    Response body:
    - **id**: id of food in foodlist
    - **title**: title of added food
    - **kcal_100g**: amount of kcal for 100g
    - **amount**: amount of added food

    """

    # Fetch food from foods table in database
    answer = db.query(models.Food).filter(models.Food.id == new_food.id_food).first()
    if answer is None:  # if no food was fetched
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")

    add_time = datetime.now()   # add timestamp
    new_food_model = models.Foodlist(id_user=curr_user.id, time=add_time, **new_food.dict())

    try:    # add to database
        db.add(new_food_model)
        db.commit()
    except IntegrityError as e:     # if constrains were violated
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:  # when other exception occured (data error)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    # fetch the response (added food)
    fetched = db.query(models.Foodlist.id, models.Food.title, models.Food.kcal_100g, models.Foodlist.amount) \
        .join(models.Food).filter(and_(models.Foodlist.id_food == new_food.id_food,
                                       models.Foodlist.id_user == curr_user.id,
                                       models.Foodlist.time == add_time)).first()

    return fetched


# DELETE endpoint for deleting food from food list
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT,
               responses={404: {'description': 'Not found'},
                          401: {'description': 'Unauthorized'}})
def delete_food_from_food_list(id: int, curr_user: models.User = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    """
    DELETE endpoint for deleting food from food list

    Query parameter:
    - **id**: id of food in foodlist

    """

    # fetch food from foodlist
    food_query = db.query(models.Foodlist).filter(models.Foodlist.id == id)
    food = food_query.first()

    if food is None:    # if no food was fetched raise an exception
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food listing not found")
    elif food.id_user != curr_user.id:  # if the food belongs to other user raise an excepion
        raise ex_notAuthToPerformAction

    food_query.delete(synchronize_session=False)    # delte the food
    db.commit()
