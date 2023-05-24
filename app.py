import random
import logging
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import not_, or_
from sqlalchemy.orm import Session
from models import Recipe, RecipeModel, BaseModel
from database import get_db
from service import fetch_image, update_nutritions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/generate-image")
def update_recipe_image(recipe_name: str = Query(...)):
    return fetch_image(recipe_name)

@app.get("/recipes/update-images")
def update_all_recipe_images(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()  # fetch all recipes
    for recipe in recipes:
        try:
            image_url = fetch_image(recipe.name)
            recipe.image = image_url
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    db.commit()
    return {"message": "Images updated for all recipes"}

@app.get("/recipes/update-nutrition")
def update_recipe_nutrition(db: Session = Depends(get_db)):
    db_recipes = db.query(Recipe).filter(or_(Recipe.nutrition == None, not_(Recipe.nutrition))).all()

    if not db_recipes:
        raise HTTPException(status_code=404, detail="Recipe not found")

    for db_recipe in db_recipes:
        db_recipe.nutrition = update_nutritions(db_recipe)
        db.commit()
        db.refresh(db_recipe)
    
    return {"message": "Nutritions updated for all recipes"}


class UpdateDescriptionRequest(BaseModel):
    description: str

@app.put("/recipes/{recipe_id}/update-description")
def update_recipe_description(recipe_id: int, request: UpdateDescriptionRequest, db: Session = Depends(get_db)):
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_recipe.description = request.description
    db.commit()
    db.refresh(db_recipe)

    return {"message": f"Description updated for recipe {recipe_id}"}

@app.post("/addrecipe/")
def add_recipe(recipe: RecipeModel, db: Session = Depends(get_db)):
    new_recipe = Recipe(**recipe.dict())
    new_recipe.nutrition = update_nutritions(new_recipe)
    db.add(new_recipe)
    db.commit()
    return {"message": "Recipe added successfully"}


@app.get("/recipes/")
def get_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).all()
    return random.sample(recipes, 3)

@app.get("/shoppinglist/{recipe_id}")
def get_shopping_list(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe:
        return {"ingredients": recipe.ingredients}
    else:
        return {"Error": "Recipe not found"}
