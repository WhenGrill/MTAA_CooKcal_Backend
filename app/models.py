from sqlalchemy import Column, ForeignKey, SmallInteger, Integer, Float, String, Text, Boolean, LargeBinary
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    profile_picture = Column(LargeBinary, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(SmallInteger, nullable=False)  # ENUM???
    age = Column(Integer, nullable=False)
    goal_weight = Column(Float)
    height = Column(Float)
    state = Column(SmallInteger)  # ENUM???
    is_nutr_adviser = Column(Boolean)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Weightmeasure(Base):
    __tablename__ = "weight_measurements"

    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    weight = Column(Float, nullable=False)
    measure_time = Column(TIMESTAMP(timezone=True), nullable=False)


class Foodlist(Base):
    __tablename__ = "food_list"

    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    id_food = Column(Integer, ForeignKey("food.id", ondelete="CASCADE"), primary_key=True)
    amount = Column(Float, nullable=False)
    time = Column(TIMESTAMP(timezone=True), nullable=False)


class Food(Base):
    __tablename__ = "food"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    kcal_100g = Column(Float, nullable=False)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    recipe_picture = Column(LargeBinary, nullable=True)
    title = Column(String, nullable=False)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    kcal_100g = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
