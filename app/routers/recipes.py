from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from ..schemas import recipes
from typing import List, Optional
from ..oauth2 import get_current_user, ex_notAuthToPerformAction
from ..utils import remove_none_from_dict, ex_formatter, verify_image
from starlette.responses import StreamingResponse
from datetime import datetime
import io
from PIL import Image

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


@router.get("/", response_model=List[recipes.RecipeOut])
def get_recipes(title: Optional[str] = '', db: Session = Depends(get_db),
                curr_user: models.User = Depends(get_current_user)):

    if title != '':
        title = title.lower()
        answer = db.query(models.Recipe).filter(func.lower(models.Recipe.title).like(f"%{title}%")).all()
    else:
        answer = db.query(models.Recipe).all()

    return answer


@router.get("/{recipe_id}", response_model=recipes.RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db),
               curr_user: models.User = Depends(get_current_user)):
    answer = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

    if answer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    return answer


@router.get("/{recipe_id}/image", response_model=recipes.RecipeOutPicture)
def get_recipe_image(recipe_id: int, db: Session = Depends(get_db),
                     curr_user: models.User = Depends(get_current_user)):
    recipe = db.query(models.Recipe.recipe_picture).filter(models.Recipe.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    elif recipe.recipe_picture is None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    else:
        im = Image.open(io.BytesIO(recipe.recipe_picture))
        return StreamingResponse(io.BytesIO(recipe.recipe_picture), media_type=f"image/{im.format.lower()}")


@router.post("/", response_model=recipes.RecipePostOut)
def add_recipe(recipe_data: recipes.RecipeIn, db: Session = Depends(get_db),
               curr_user: models.User = Depends(get_current_user)):
    time = datetime.now()
    new_recipe = models.Recipe(id_user=curr_user.id, created_at=time, **recipe_data.dict())

    try:
        db.add(new_recipe)
        db.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    fetched = db.query(models.Recipe.id, models.Recipe.title, models.Recipe.id_user, models.Recipe.created_at).filter \
        (and_(models.Recipe.id == new_recipe.id,
              models.Recipe.id_user == curr_user.id,
              models.Recipe.created_at == time)).first()

    return fetched


@router.put("/{id}", response_model=recipes.RecipeOut)
def update_recipe(id: int, updated_recipe: recipes.RecipeUpdate, db: Session = Depends(get_db),
                  curr_user: models.User = Depends(get_current_user)):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    elif recipe.id_user != curr_user.id:
        raise ex_notAuthToPerformAction

    try:
        recipe_query.update(remove_none_from_dict(updated_recipe.dict()), synchronize_session=False)
        db.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    return recipe_query.first()


@router.put("/{id}/image")
def update_recipe_picture(id: int, updated_profile_picture: UploadFile = File(...),
                          curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recipe with id {id} was not found")
    elif recipe.id_user != curr_user.id:
        raise ex_notAuthToPerformAction

    verified_image = verify_image(updated_profile_picture.file.read())

    recipe_query.update({"recipe_picture": verified_image}, synchronize_session=False)
    db.commit()

    return StreamingResponse(io.BytesIO(recipe_query.first().recipe_picture), media_type="image/png")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(id: int, curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    elif recipe.id_user != curr_user.id:
        raise ex_notAuthToPerformAction

    recipe_query.delete(synchronize_session=False)
    db.commit()
