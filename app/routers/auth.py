from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, models, utils, oauth2


router = APIRouter(tags=["Authentification"])


@router.post('/login', response_model=schemas.TokenResponse)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise oauth2.ex_InvalidCreds

    if not utils.verify(user_credentials.password, user.password):
        raise oauth2.ex_InvalidCreds

    # Create token
    access_token = oauth2.create_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}