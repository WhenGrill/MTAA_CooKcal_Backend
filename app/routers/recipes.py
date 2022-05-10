from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from ..database import get_db, ws_get_db
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

# Recipe router init
router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
    responses={401: {'description': 'Unauthorized'}}
)


# GET endpoint for getting recipes based on title
@router.get("/", response_model=List[recipes.RecipeOut], status_code=status.HTTP_200_OK)
def get_recipes(title: Optional[str] = '', db: Session = Depends(get_db),
                curr_user: models.User = Depends(get_current_user)):
    """
    **GET endpoint for getting recipes based on title**

    Query parameter:
    - Optional **title**: title of recipe, if empty returns every recipe

    Response body:
    - **id**: recipe id
    - **title**: recipe title
    - **ingredients**: ingredients of recipe
    - **instructions**: instructions of recipe
    - **kcal_100g**: kcal of recipe
    - **creator**: creator of current recipe

    Creator body:
    - **id**: id of recipes owner
    - **first_name**: Name of creator (user)
    - **last_name**: Lastname of creator (user)
    - **gender**: creator's gender
    - **age**: creator's gender
    - **state**: creator's gender
    - **is_nutr_adviser**: boolean if creator is nutritional adviser

    """

    if title != '':  # if title is empty string, get every recipe
        title = title.lower()
        answer = db.query(models.Recipe).filter(func.lower(models.Recipe.title).like(f"%{title}%")).all()
    else:  # else get recipe based on title
        answer = db.query(models.Recipe).all()

    return answer


@router.websocket("/ws")
async def ws_get_recipes(websocket: WebSocket):
    await websocket.accept()
    token: str = websocket.headers['authorization']
    db = ws_get_db()
    curr_user = get_current_user(token=token, db=db, is_wb=True)

    if not isinstance(curr_user, models.User):
        return curr_user

    try:
        while True:
            title: str = await websocket.receive_text()

            if title != '':  # if title is empty string, get every recipe
                title = title.lower()
                answer = db.query(models.Recipe).filter(func.lower(models.Recipe.title).like(f"%{title}%")).all()
            else:  # else get recipe based on title
                answer = db.query(models.Recipe).all()

            l_recipes = []
            for x in answer:
                user = db.query(models.User).filter(models.User.id == x.id_user).first()
                merge_dict = x.__dict__
                merge_dict['creator'] = user.__dict__
                new = recipes.RecipeOut(**merge_dict)
                l_recipes.append(new.dict())


            await websocket.send_json({'status_code': 200, 'detail': l_recipes})

    except WebSocketDisconnect:
        pass


# GET endpoint for getting a recipe based on its id
@router.get("/{id}", response_model=recipes.RecipeOut, status_code=status.HTTP_200_OK,
            responses={404: {'description': 'Not found'}})
def get_recipe(id: int, db: Session = Depends(get_db),
               curr_user: models.User = Depends(get_current_user)):

    """
    **GET endpoint for getting a recipe based on its id**

    Request body:
    - **id**: id of recipe

    Response body:
    - **id**: recipe id
    - **title**: recipe title
    - **ingredients**: ingredients of recipe
    - **instructions**: instructions of recipe
    - **kcal_100g**: kcal of recipe
    - **creator**: creator of current recipe

    Creator body:
    - **id**: id of recipes owner
    - **first_name**: Name of creator (user)
    - **last_name**: Lastname of creator (user)
    - **gender**: creator's gender
    - **age**: creator's gender
    - **state**: creator's gender
    - **is_nutr_adviser**: boolean if creator is nutritional adviser

    """

    answer = db.query(models.Recipe).filter(models.Recipe.id == id).first()

    if answer is None:  # if no recipe was fetched raise exception
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    return answer


# GET endpoint for getting a recipe's image
@router.get("/{id}/image", status_code=status.HTTP_200_OK,
            responses={204: {'description': 'No content'},
                       404: {'description': 'Not found'}}
            )
def get_recipe_image(id: int, db: Session = Depends(get_db),
                     curr_user: models.User = Depends(get_current_user)):

    """
    **GET endpoint for getting a recipe's image**

    Query parameter:
    - **id**: id of recipe

    Response body:
    - **Recipe picture**

    """

    recipe = db.query(models.Recipe.recipe_picture).filter(models.Recipe.id == id).first()

    if recipe is None:  # if no recipe was fetched raise exception
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")

    elif recipe.recipe_picture is None:  # if recipe was fetched but has no picture raise an exception
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    else:  # else display the picture
        im = Image.open(io.BytesIO(recipe.recipe_picture))
        return StreamingResponse(io.BytesIO(recipe.recipe_picture), media_type=f"image/{im.format.lower()}")


# POST endpoint for adding a new recipe
@router.post("/", response_model=recipes.RecipePostOut, status_code=status.HTTP_201_CREATED,
             responses={403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'}})
def add_recipe(recipe_data: recipes.RecipeIn, db: Session = Depends(get_db),
               curr_user: models.User = Depends(get_current_user)):

    """
    **POST endpoint for adding a new recipe**

    Request body:
    - **title**: title of recipe of recipe
    - **ingredients**: ingredients to recipe
    - **instructions**: instructions to recipe
    - **kcal_100g**: kcal of food

    Response body:
    - **id**: recipe id
    - **id_user**: user's id
    - **title**: title of recipe of recipe
    - **created_at**: time of recipe creation

    """

    time = datetime.now()
    new_recipe = models.Recipe(id_user=curr_user.id, created_at=time, **recipe_data.dict())  # create a new recipe

    try:
        db.add(new_recipe)  # add it to database
        db.commit()
    except IntegrityError as e:  # when constrains in databse were violated
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:  # when other exception occured (data error)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    # fetch the added recipe and return it
    fetched = db.query(models.Recipe.id, models.Recipe.title, models.Recipe.id_user, models.Recipe.created_at).filter \
        (and_(models.Recipe.id == new_recipe.id,
              models.Recipe.id_user == curr_user.id,
              models.Recipe.created_at == time)).first()

    return fetched


# PUT endpoint for recipe update
@router.put("/{id}", response_model=recipes.RecipeOut, status_code=status.HTTP_200_OK,
            responses={304: {'description': 'Not modified - Nothing to update'},
                       401: {'description': 'Unauthorized'},
                       403: {'description': 'Forbidden - Integrity or Data error (violated DB constraints)'},
                       404: {'description': 'Not found'}})
def update_recipe(id: int, updated_recipe: recipes.RecipeUpdate, db: Session = Depends(get_db),
                  curr_user: models.User = Depends(get_current_user)):

    """
    **PUT endpoint for recipe update**

    Request body:
    - Optional **title**: title of recipe of recipe
    - Optional **ingredients**: ingredients to recipe
    - Optional **instructions**: instructions to recipe
    - Optional **kcal_100g**: kcal of food

    Response body:
    - **id**: recipe id
    - **title**: recipe title
    - **ingredients**: ingredients of recipe
    - **instructions**: instructions of recipe
    - **kcal_100g**: kcal of recipe
    - **creator**: creator of current recipe

    Creator body:
    - **id**: id of recipes owner
    - **first_name**: Name of creator (user)
    - **last_name**: Lastname of creator (user)
    - **gender**: creator's gender
    - **age**: creator's gender
    - **state**: creator's gender
    - **is_nutr_adviser**: boolean if creator is nutritional adviser

    """

    # fetch the recipe
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:  # if no recipe was fecthed raise an exception
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    elif recipe.id_user != curr_user.id:  # if the recipe belongs to other user raise an exception
        raise ex_notAuthToPerformAction
    elif all(value is None for value in updated_recipe.dict().values()):  # if there is no value to update (empty json)
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Nothing to update")

    try:  # update the recipe
        recipe_query.update(remove_none_from_dict(updated_recipe.dict()), synchronize_session=False)
        db.commit()
    except IntegrityError as e:  # if constrains in database were violated raise an exception
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ex_formatter(e))
    except Exception as e:  # if other exception occured (data error)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.__cause__))

    # return updated recipe
    return recipe_query.first()


# PUT endpoint for updating recipe image
@router.put("/{id}/image", status_code=status.HTTP_200_OK,
            responses={404: {'description': 'Not found'},
                       413: {'description': 'Request entity too large (exceeded 2.7MB)'},
                       415: {'description': 'Unsupported media type'}})
def update_recipe_picture(id: int, recipe_picture: UploadFile = File(...),
                          curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    """
    **PUT endpoint for updating recipe image**

    Query parameter:
    - **id**: id of recipe

    Request body:
    - **Recipe picture** in form data

    Response body:
    - **Recipe picture**

    """

    # fetch the recipe
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:  # if no recipe was fetched raise an excepton
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recipe with id {id} was not found")
    elif recipe.id_user != curr_user.id:    # if the fecthed recipe belongs to another user raise an exception
        raise ex_notAuthToPerformAction

    verified_image = verify_image(recipe_picture.file.read())  # verify that the file is an image

    # update database
    recipe_query.update({"recipe_picture": verified_image}, synchronize_session=False)
    db.commit()

    return StreamingResponse(io.BytesIO(recipe_query.first().recipe_picture), media_type="image/png")


# DELETE endpoint for recipe
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT,
               responses={404: {'description': 'Not found'}})
def delete_recipe(id: int, curr_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    """
    DELETE endpoint for recipe

    Query parameter:
    - **id**: id of recipe

    """

    # fetch the recipe
    recipe_query = db.query(models.Recipe).filter(models.Recipe.id == id)
    recipe = recipe_query.first()

    if recipe is None:  # if no recipe was fetched
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    elif recipe.id_user != curr_user.id:    # if the recipe belongs to another user raise an exception
        raise ex_notAuthToPerformAction

    # delete the recipe
    recipe_query.delete(synchronize_session=False)
    db.commit()
