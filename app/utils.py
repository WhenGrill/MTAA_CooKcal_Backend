from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def pwd_hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password: str, hashed_password: str):  # Verify if password matches with hash in DB
    return pwd_context.verify(plain_password, hashed_password)
