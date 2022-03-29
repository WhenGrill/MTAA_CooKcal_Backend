from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from .. import models
from ..schemas.weight_measurement import WeightIn, WeightOut
from typing import List, Optional
from ..oauth2 import get_current_user
from dateutil import parser
from ..utils import ex_formatter

# Authentification router init
router = APIRouter(
    prefix="/weight_measurement",
    tags=["Weight measurement"],
    responses={401: {'description': 'Unauthorized'}}
)


# GET endpoint for getting weight measurement based on date
@router.get("/", response_model=List[WeightOut], status_code=status.HTTP_200_OK)
def get_weight_measurement(date: Optional[str] = '', db: Session = Depends(get_db),
                           curr_user: models.User = Depends(get_current_user)):

    """
    **GET endpoint for getting weight measurement based on date**

    Query patameter:
    - Optional **date**: date of measuremnts, if empty fetches every weight measurement of current user

    Response body:
    - **weight**: inserted weight
    - **measure_time**: time of weight measurement

    """

    if date == '':  # if no date was provided return every measuremnt of current user
        answer = db.query(models.Weightmeasure).filter(models.Weightmeasure.id_user == curr_user.id).all()
    else:
        try:  # check if date is valid
            date = str(parser.parse(date).date())
        except Exception:
            return []

        # fetch weight measurement
        answer = db.query(models.Weightmeasure).filter((func.date(models.Weightmeasure.measure_time) >= date),
                                                       func.date(models.Weightmeasure.measure_time) <= date).all()

    return answer


# POST endpoint for adding new weight measurement
@router.post("/", response_model=WeightOut, status_code=status.HTTP_200_OK,
             responses={403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'}})
def add_weight_measurement(weight: WeightIn, db: Session = Depends(get_db),
                           curr_user: models.User = Depends(get_current_user)):
    """
        **POST endpoint for adding new weight measurement**

        Request body:
        - **weight**, weight measurement to be added

        Response body:
        - **weight**: inserted weight
        - **measure_time**: time of weight measurement

        """

    # get curent datetime and create new weigh measurement
    time = datetime.now()
    new_measurement = models.Weightmeasure(id_user=curr_user.id, measure_time=time, **weight.dict())
    try:    # add to database
        db.add(new_measurement)
        db.commit()
    except IntegrityError as e:     # if database constrains were violated raise an exception
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:  # when other exception occured (data error)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    # fetch added weight measurement
    fetched = db.query(models.Weightmeasure.weight, models.Weightmeasure.measure_time).filter \
        (and_(models.Weightmeasure.id_user == curr_user.id,
              models.Weightmeasure.measure_time == time)).first()

    return fetched
