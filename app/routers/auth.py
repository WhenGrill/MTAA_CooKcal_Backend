from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, utils, oauth2
from ..schemas.users import TokenResponse

# Authentification router init
router = APIRouter(tags=["Authentification"],
                   responses={403: {'description': 'Forbidden - Invalid credentials'}})


# POST endpoint for user login
@router.post('/login', response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # GET user from database
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    # If no user was fetched form database
    if not user:
        raise oauth2.ex_InvalidCreds

    # If user verifycation did not succeed
    if not utils.verify(user_credentials.password, user.password):
        raise oauth2.ex_InvalidCreds

    # Create token
    access_token = oauth2.create_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
