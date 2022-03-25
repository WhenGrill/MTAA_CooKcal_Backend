from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models
from ..schemas import weight_measurement
from typing import List, Optional
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..utils import remove_none_from_dict
from starlette.responses import StreamingResponse
import io

router = APIRouter(
    prefix="/weight_measurement",
    tags=["Weight_measurement"]
)


@router.get("/", response_model=List[weight_measurement.WeightOut])
def get_weight_measurement(date: Optional[str] = '', db: Session = Depends(get_db),
                           curr_user: models.User = Depends(get_current_user)):
    if date == '':
        answer = db.query(models.Weightmeasure).filter(models.Weightmeasure.id_user == curr_user.id).all()
    else:
        answer = db.query(models.Weightmeasure).filter((func.date(models.Weightmeasure.measure_time) >= date),
                                                       func.date(models.Weightmeasure.measure_time) <= date).all()

    return answer


# Still not working
@router.post("/", response_model=weight_measurement.WeightOut)
def add_recipe(weight: weight_measurement.WeightIn, db: Session = Depends(get_db),
               curr_user: models.User = Depends(get_current_user)):
    new_measurement = models.Weightmeasure(id_user=curr_user.id, **weight.dict())
    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)

    return new_measurement