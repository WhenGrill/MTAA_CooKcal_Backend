from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..schemas import recipes
from typing import List, Optional
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..utils import remove_none_from_dict
from starlette.responses import StreamingResponse
import io

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


@router.get("/", response_model=List[recipes.RecipeOut])
def get_recipes(title: Optional[str] = '', db: Session = Depends(get_db),
                curr_user: models.User = Depends(get_current_user)):
    if title != '':
        answer = db.query(models.Recipe).filter(models.Recipe.title == title).all()
    else:
        answer = db.query(models.Recipe).all()

    return answer


@router.get("/{recipe_id}", response_model=recipes.RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db),
               curr_user: models.User = Depends(get_current_user)):
    answer = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    return answer


@router.get("/{recipe_id}/image", response_model=recipes.RecipeOutPicture)
def get_recipe_image(recipe_id: int, db: Session = Depends(get_db),
                     curr_user: models.User = Depends(get_current_user)):
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


@router.put("/{id}", response_model=recipes.RecipeOut)
def update_recipe(id: int, updated_recipe: recipes.RecipeUpdate, db: Session = Depends(get_db),
                  curr_user: models.User = Depends(get_current_user)):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    if recipe.user_id != curr_user.id:
        raise ex_notAuthToPerformAction

    recipe_query.update(remove_none_from_dict(updated_recipe.dict()), synchronize_session=False)
    db.commit()

    return recipe_query.first()


@router.put("/{id}/image")
def update_recipe_picture(id: int, updated_profile_picture: recipes.RecipeInPicture,
                                curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recipe with id {id} was not found")
    elif recipe.user_id != curr_user.id:
        raise ex_notAuthToPerformAction

    recipe_query.update(remove_none_from_dict(updated_profile_picture.dict()), synchronize_session=False)
    db.commit()

    return StreamingResponse(io.BytesIO(recipe_query.first().profile_picture.tobytes()), media_type="image/png")
