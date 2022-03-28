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
    tags=["Recipes"],
    responses={401: {'description': 'Unauthorized'}}
)


@router.get("/", response_model=List[recipes.RecipeOut], status_code=status.HTTP_200_OK)
def get_recipes(title: Optional[str] = '', db: Session = Depends(get_db),
                curr_user: models.User = Depends(get_current_user)):

    if title != '':
        title = title.lower()
        answer = db.query(models.Recipe).filter(func.lower(models.Recipe.title).like(f"%{title}%")).all()
    else:
        answer = db.query(models.Recipe).all()

    return answer


@router.get("/{id}", response_model=recipes.RecipeOut, status_code=status.HTTP_200_OK,
            responses={404: {'description': 'Not found'}})
def get_recipe(id: int, db: Session = Depends(get_db),
               curr_user: models.User = Depends(get_current_user)):
    answer = db.query(models.Recipe).filter(models.Recipe.id == id).first()

    if answer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    return answer


@router.get("/{id}/image", response_model=recipes.RecipeOutPicture, status_code=status.HTTP_200_OK,
            responses={204: {'description': 'No content'},
                       404: {'description': 'Not found'}}
            )
def get_recipe_image(id: int, db: Session = Depends(get_db),
                     curr_user: models.User = Depends(get_current_user)):
    recipe = db.query(models.Recipe.recipe_picture).filter(models.Recipe.id == id).first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    elif recipe.recipe_picture is None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    else:
        im = Image.open(io.BytesIO(recipe.recipe_picture))
        return StreamingResponse(io.BytesIO(recipe.recipe_picture), media_type=f"image/{im.format.lower()}")


@router.post("/", response_model=recipes.RecipePostOut, status_code=status.HTTP_200_OK,
             responses={403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'}})
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


@router.put("/{id}", response_model=recipes.RecipeOut, status_code=status.HTTP_200_OK,
            responses={304: {'description': 'Not modified - Nothing to update'},
                       401: {'description': 'Unauthorized'},
                       403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'},
                       404: {'description': 'Not found'}})
def update_recipe(id: int, updated_recipe: recipes.RecipeUpdate, db: Session = Depends(get_db),
                  curr_user: models.User = Depends(get_current_user)):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    elif recipe.id_user != curr_user.id:
        raise ex_notAuthToPerformAction
    elif all(value is None for value in updated_recipe.dict().values()):
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Nothing to update")

    try:
        recipe_query.update(remove_none_from_dict(updated_recipe.dict()), synchronize_session=False)
        db.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    return recipe_query.first()


@router.put("/{id}/image", status_code=status.HTTP_200_OK,
            responses={404: {'description': 'Not found'},
                       413: {'description': 'Request entity too large (exceeded 2.7MB)'},
                       415: {'description': 'Unsupported media type'}})
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT,
               responses={404: {'description': 'Not found'}})
def delete_recipe(id: int, curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    elif recipe.id_user != curr_user.id:
        raise ex_notAuthToPerformAction

    recipe_query.delete(synchronize_session=False)
    db.commit()
