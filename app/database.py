from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import env

# code for session establishment with database
SQLALCHEMY_DATABASE_URL = f'postgresql://{env.database_username}:{env.database_password}@' \
                          f'{env.database_hostname}:{env.database_port}/{env.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ws_get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        return None
