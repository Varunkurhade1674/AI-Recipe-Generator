"""
SQLAlchemy ORM models for the AI Recipe Generator.

Only generated recipes are persisted. Groq API keys are NEVER stored here.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func

from database.database import Base


class Recipe(Base):
    """Represents a single AI-generated recipe saved by a user."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    recipe_name = Column(String(255), nullable=False)
    emoji = Column(String(10), nullable=True)
    cuisine = Column(String(100), nullable=True)
    meal_type = Column(String(100), nullable=True)
    diet_preference = Column(String(100), nullable=True)
    difficulty = Column(String(50), nullable=True)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    prep_time = Column(String(50), nullable=True)
    cooking_time = Column(String(50), nullable=True)
    calories = Column(String(50), nullable=True)
    protein = Column(String(50), nullable=True)
    carbs = Column(String(50), nullable=True)
    fat = Column(String(50), nullable=True)
    cooking_tips = Column(Text, nullable=True)
    storage_tips = Column(Text, nullable=True)
    alternative_ingredients = Column(Text, nullable=True)
    serving_suggestions = Column(Text, nullable=True)
    raw_markdown = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self) -> dict:
        """Serialize the recipe to a plain dict for JSON responses / templates."""
        return {
            "id": self.id,
            "recipe_name": self.recipe_name,
            "emoji": self.emoji,
            "cuisine": self.cuisine,
            "meal_type": self.meal_type,
            "diet_preference": self.diet_preference,
            "difficulty": self.difficulty,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "description": self.description,
            "prep_time": self.prep_time,
            "cooking_time": self.cooking_time,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fat": self.fat,
            "cooking_tips": self.cooking_tips,
            "storage_tips": self.storage_tips,
            "alternative_ingredients": self.alternative_ingredients,
            "serving_suggestions": self.serving_suggestions,
            "raw_markdown": self.raw_markdown,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
