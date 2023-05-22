from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ingredients = Column(String)
    steps = Column(String)
    image = Column(String, nullable=True)
    nutrition = Column(JSON, nullable=True)

class RecipeModel(BaseModel):
    name: str
    ingredients: str
    steps: str
    image: str = None
    nutrition: str = None
