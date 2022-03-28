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

router = APIRouter(
    prefix="/weight_measurement",
    tags=["Weight measurement"],
    responses={401: {'description': 'Unauthorized'}}
)


@router.get("/", response_model=List[WeightOut], status_code=status.HTTP_200_OK)
def get_weight_measurement(date: Optional[str] = '', db: Session = Depends(get_db),
                           curr_user: models.User = Depends(get_current_user)):

    if date == '':
        answer = db.query(models.Weightmeasure).filter(models.Weightmeasure.id_user == curr_user.id).all()
    else:
        try:
            date = str(parser.parse(date).date())
        except Exception:
            return []

        answer = db.query(models.Weightmeasure).filter((func.date(models.Weightmeasure.measure_time) >= date),
                                                       func.date(models.Weightmeasure.measure_time) <= date).all()

    return answer


@router.post("/", response_model=WeightOut, status_code=status.HTTP_200_OK,
             responses={403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'}})
def add_weight_measurement(weight: WeightIn, db: Session = Depends(get_db),
                           curr_user: models.User = Depends(get_current_user)):
    time = datetime.now()
    new_measurement = models.Weightmeasure(id_user=curr_user.id, measure_time=time, **weight.dict())
    try:
        db.add(new_measurement)
        db.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    fetched = db.query(models.Weightmeasure.weight, models.Weightmeasure.measure_time).filter \
        (and_(models.Weightmeasure.id_user == curr_user.id,
              models.Weightmeasure.measure_time == time)).first()

    return fetched
