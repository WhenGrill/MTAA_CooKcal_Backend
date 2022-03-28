from pydantic import BaseModel
import datetime


# Adding weight measurement schema
class WeightIn(BaseModel):
    weight: float


# Response for added weight
class WeightOut(BaseModel):
    weight: float
    measure_time: datetime.datetime

    class Config:
        orm_mode = True
