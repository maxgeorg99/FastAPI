import requests
from cachetools import cached, TTLCache
from fastapi import HTTPException

cache = TTLCache(maxsize=100, ttl=3600)
UNSPLASH_ACCESS_KEY = "2vnckh7icD1yi6_-IZghWGjfVwQz0TP7XLqu_D2MtSQ"

@cached(cache)
def fetch_image(recipe_name: str):
    response = requests.get(
        "https://api.unsplash.com/photos/random",
        params={"query": recipe_name, "count": 1},
        headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
        timeout=500
    )
    data = response.json()
    if not data:
        raise HTTPException(status_code=404, detail="Image not found")
    return data[0]["urls"]["small"]

def get_nutrition_info(ingredient_name: str):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        "query": ingredient_name,
        "pageSize": 1,
        "api_key": "W5YlwWjrnNHkHtKpXv9J81e5RDRKdHyi2Jy7DtOs"
    }

    response = requests.get(url, params=params, timeout=5000)
    data = response.json()

    if "foods" in data and data["foods"]:
        food = data["foods"][0]
        nutrients = food["foodNutrients"]

        nutrition_info = {
            "calories": None,
            "fat": None,
            "protein": None,
            "carbs": None
        }

        for nutrient in nutrients:
            if nutrient["nutrientName"] == "Energy":
                nutrition_info["calories"] = nutrient["value"]
            elif nutrient["nutrientName"] == "Total lipid (fat)":
                nutrition_info["fat"] = nutrient["value"]
            elif nutrient["nutrientName"] == "Protein":
                nutrition_info["protein"] = nutrient["value"]
            elif nutrient["nutrientName"] == "Carbohydrate, by difference":
                nutrition_info["carbs"] = nutrient["value"]

        return nutrition_info

    return None
