from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..schemas import recipes
from typing import List, Optional
from ..oauth2 import get_current_user, ex_validationErr

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


@router.get("/", response_model=List[recipes.RecipeOut])
def get_recipes(title: Optional[str] = '', db: Session = Depends(get_db)):
    if title != '':
        answer = db.query(models.Recipe).filter(models.Recipe.title == title).all()
    else:
        answer = db.query(models.Recipe).all()

    return answer


@router.get("/{recipe_id}", response_model=recipes.RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    answer = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    return answer


@router.get("/{recipe_id}/image", response_model=recipes.RecipeOutPicture)
def get_recipe_image(recipe_id: int, db: Session = Depends(get_db)):
    answer = db.query(models.Recipe.recipe_picture).filter(models.Recipe.id == recipe_id).first()

    return answer


# still not working
@router.post("/", response_model=recipes.RecipeOut)
def add_recipe(recipe_data: recipes.RecipeIn, db: Session = Depends(get_db),
               curr_user: models.User = Depends(get_current_user)):
    new_recipe = models.Recipe(user_id=curr_user.id, **recipe_data.dict())
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    return recipe_data
