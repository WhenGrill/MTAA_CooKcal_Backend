from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from . import database, models
from .schemas.users import TokenData
from sqlalchemy.orm import Session
from .config import env

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ex_InvalidCreds = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
ex_validationErr = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail=f"Could not validate credentials",
                                 headers={"WWW-Authenticate": "Bearer"})

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


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> models.User:
    token = verify_token(token, ex_validationErr)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
