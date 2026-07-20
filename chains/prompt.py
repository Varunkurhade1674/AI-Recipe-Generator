"""
LangChain PromptTemplate definitions for recipe generation.

This module demonstrates LangChain concept #1: PromptTemplate.
Keeping the prompt separate from the chain wiring (recipe_chain.py) keeps
prompt engineering isolated and easy to iterate on.
"""

from langchain_core.prompts import PromptTemplate

RECIPE_SYSTEM_INSTRUCTIONS = """You are a professional chef and certified nutritionist \
who writes clear, structured, easy-to-follow recipes for home cooks."""

RECIPE_PROMPT_TEMPLATE = """{system_instructions}

Create a complete, professional recipe using the details below.

Ingredients available: {ingredients}
Cuisine: {cuisine}
Meal type: {meal_type}
Diet preference: {diet_preference}
Difficulty level: {difficulty}
Target cooking time: {cooking_time}

Requirements:
- Instructions must be simple, numbered, and easy for a home cook to follow.
- Provide sensible ingredient substitutions where relevant.
- Provide realistic estimated nutritional values (do not skip this section).
- Use clear structured formatting with the EXACT section headers below.
- Do not include any text before "RECIPE_NAME:" or after "SERVING_SUGGESTIONS:".

Respond using EXACTLY this structure (plain text, keep the headers as-is):

RECIPE_NAME: <name of the dish>
DISH_EMOJI: <Pick exactly ONE cooked meal emoji from this list: 🍲, 🥘, 🍝, 🍛, 🥗, 🍜, 🍔, 🍕, 🌮, 🌯, 🥪, 🥧, 🍰, 🥞, 🥩, 🍱, 🍛, 🍣. DO NOT use raw ingredients like 🍅 or 🐔!>
DESCRIPTION: <2-3 sentence appetizing description>
PREP_TIME: <e.g. 15 minutes>
COOKING_TIME: <e.g. 30 minutes>
CALORIES: <estimated kcal per serving>
PROTEIN: <grams per serving>
CARBS: <grams per serving>
FAT: <grams per serving>
INGREDIENTS:
- <ingredient with quantity>
- <ingredient with quantity>
INSTRUCTIONS:
1. <step>
2. <step>
COOKING_TIPS: <2-3 practical tips>
STORAGE_TIPS: <how to store and for how long>
ALTERNATIVE_INGREDIENTS: <substitution suggestions>
SERVING_SUGGESTIONS: <what to pair or serve it with>
"""


def build_recipe_prompt() -> PromptTemplate:
    """
    Build and return the reusable PromptTemplate used for recipe generation.

    Using PromptTemplate (instead of an f-string) is what lets this plug
    directly into an LCEL RunnableSequence via the `|` operator.
    """
    return PromptTemplate(
        input_variables=[
            "ingredients",
            "cuisine",
            "meal_type",
            "diet_preference",
            "difficulty",
            "cooking_time",
        ],
        partial_variables={"system_instructions": RECIPE_SYSTEM_INSTRUCTIONS},
        template=RECIPE_PROMPT_TEMPLATE,
    )
