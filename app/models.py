from sqlalchemy import Column, ForeignKey, SmallInteger, Integer, Float, String, Text, Boolean, LargeBinary
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

from .database import Base


# User table model
class User(Base):
    __tablename__ = "users"

    # columns
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    profile_picture = Column(LargeBinary, nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    gender = Column(SmallInteger, nullable=False)
    age = Column(SmallInteger, nullable=False)
    goal_weight = Column(Float)
    height = Column(Float)
    state = Column(SmallInteger)
    is_nutr_adviser = Column(Boolean)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # constrains
    __table_args__ = (UniqueConstraint('email'),
                      CheckConstraint("email ~ '^.+[@]{1}.+[.]{1}.+$' ", name='valid_email'),
                      CheckConstraint('gender BETWEEN 0 AND 2', name='gender_between_0_and_2'),
                      CheckConstraint('age > 0 AND age < 120', name='age_between_1_and_120'),
                      CheckConstraint('goal_weight > 0', name='positive_goal_weight'),
                      CheckConstraint('height > 0', name='positive_height'),
                      CheckConstraint('state BETWEEN 0 AND 2', name='state_between_0_and_2'),
                      CheckConstraint('LENGTH(first_name) >= 2', name='first_name_minimum_characters'),
                      CheckConstraint('LENGTH(last_name) >= 2', name='last_name_minimum_characters'),
                      )


# Weight measurement table
class Weightmeasure(Base):
    __tablename__ = "weightmeasurements"

    # Columns
    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    weight = Column(Float, nullable=False)
    measure_time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # constrains
    __tableargs__ = (CheckConstraint('weight > 0', name='positive_weight'),)


# Foodlist table
class Foodlist(Base):
    __tablename__ = "foodlist"

    # Columns
    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    id_food = Column(Integer, ForeignKey("food.id", ondelete="CASCADE"), primary_key=True)
    amount = Column(Float, nullable=False)
    time = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # Constrains
    __tableargs__ = (CheckConstraint('amount > 0', name='positive_amount'),)


# Food table
class Food(Base):
    __tablename__ = "food"

    # Columns
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(80), nullable=False)
    kcal_100g = Column(Float, nullable=False)

    # Constrains
    __tableargs__ = (CheckConstraint('kcal_100g > 0', name='positive_kcal_100g_in_food'),
                     CheckConstraint('LENGTH(title) >= 2', name='food_title_minimum_characters'),
                     )


# Recipe table
class Recipe(Base):
    __tablename__ = "recipes"

    # Columns
    id = Column(Integer, primary_key=True, nullable=False)
    id_user = Column(Integer, ForeignKey("users.id", ondelete="SET DEFAULT"), server_default=text('0'))
    recipe_picture = Column(LargeBinary, nullable=True)
    title = Column(String(80), nullable=False)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    kcal_100g = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    creator = relationship("User")  # reliationship defined

    # Constrains
    __tableargs__ = (CheckConstraint('kcal_100g >= 0', name='zero_or_positive_kcal_100g'),
                     CheckConstraint('LENGTH(title) >= 2', name='recipe_title_minimum_characters'),
                     )
