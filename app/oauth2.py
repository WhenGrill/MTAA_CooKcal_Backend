from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from . import database, models
from .schemas.users import TokenData
from sqlalchemy.orm import Session
from .config import env

# code inspired by this documentation: https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ex_InvalidCreds = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
ex_validationErr = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail=f"Could not validate credentials",
                                 headers={"WWW-Authenticate": "Bearer"})
ex_notAuthToPerformAction = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Not authorized to perform requested action")

SECRET_KEY = env.secret
ALGORITHM = env.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = env.access_token_expire_minutes


def create_token(data: dict):  # Data -> JWT payload
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # When token expires
    to_encode.update({"exp": expire})  # Expiration field

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Create JWT token
    return encoded_jwt


def verify_token(token: str, credentials_exception: HTTPException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode token
        user_id: str = payload.get("user_id")

        if not user_id:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception

    return token_data


def wb_verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode token
        user_id: str = payload.get("user_id")
        if not user_id:
            return {'status_code': 401, 'detail': "Could not validate credentials"}
        token_data = TokenData(id=user_id)
    except JWTError:
        return {'status_code': 401, 'detail': "Could not validate credentials"}

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db),
                     is_wb: bool = False) -> models.User:
    if is_wb:
        token = wb_verify_token(token)
        user = db.query(models.User).filter(models.User.id == token.id).first()
        if user is None:
            raise {'status_code': 401, 'detail': "Not authorized to perform requested action"}
    else:
        token = verify_token(token, ex_validationErr)
        user = db.query(models.User).filter(models.User.id == token.id).first()
        if user is None:
            raise ex_notAuthToPerformAction

    return user
