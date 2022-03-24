from pydantic import BaseModel
import datetime


class WeightIn(BaseModel):
    weight: float


class WeightOut(BaseModel):
    weight: float
    measure_time: datetime.datetime

    class Config:
        orm_mode = True
