"""
LangChain recipe generation chain.

Demonstrates:
  - ChatGroq                (the LLM)
  - PromptTemplate           (imported from prompt.py)
  - RunnableSequence (LCEL)  (prompt | llm | parser, built with the `|` operator)
  - StrOutputParser          (extracts the plain string content from the AIMessage)
"""

import re

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from chains.prompt import build_recipe_prompt


def build_recipe_chain(provider: str, api_key: str):
    """
    Construct the full LCEL RunnableSequence:

        PromptTemplate -> ChatModel -> StrOutputParser

    A fresh Chat model instance is created per-request using the caller's own
    verified session API key (never a hardcoded/shared key).
    """
    if provider == "Groq":
        llm = ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=1800)
    elif provider == "OpenAI":
        llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0.7, max_tokens=1800)
    elif provider == "Anthropic":
        llm = ChatAnthropic(api_key=api_key, model="claude-3-haiku-20240307", temperature=0.7, max_tokens=1800)
    elif provider == "Gemini":
        llm = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-1.5-pro", temperature=0.7, max_output_tokens=1800)
    elif provider == "OpenRouter":
        llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model="meta-llama/llama-3.3-70b-instruct",
            temperature=0.7,
            max_tokens=1800
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

    prompt = build_recipe_prompt()
    parser = StrOutputParser()

    # LCEL RunnableSequence built with the pipe operator.
    chain = prompt | llm | parser
    return chain


def generate_recipe(provider: str, api_key: str, form_data: dict) -> dict:
    """
    Run the LCEL chain with the given form data and parse the structured
    text response into a dictionary ready for the DB / template layer.
    """
    chain = build_recipe_chain(provider, api_key)

    raw_output: str = chain.invoke(
        {
            "ingredients": form_data["ingredients"],
            "cuisine": form_data.get("cuisine") or "Any",
            "meal_type": form_data.get("meal_type") or "Any",
            "diet_preference": form_data.get("diet_preference") or "None",
            "difficulty": form_data.get("difficulty") or "Medium",
            "cooking_time": form_data.get("cooking_time") or "Flexible",
        }
    )

    parsed = _parse_recipe_output(raw_output)
    parsed["raw_markdown"] = _to_markdown(parsed, raw_output)
    return parsed


def _parse_recipe_output(text: str) -> dict:
    """
    Defensively parse the structured plain-text response produced by the LLM
    into a dictionary. Falls back gracefully if a section is missing or the
    model deviates slightly from the requested format.
    """
    def _extract(pattern: str, default: str = "") -> str:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else default

    recipe_name = _extract(r"RECIPE_NAME:\s*(.+)", "Untitled Recipe")
    dish_emoji_raw = _extract(r"DISH_EMOJI:\s*([^\n]+)", "🍽️")
    description = _extract(r"DESCRIPTION:\s*(.+?)(?=\n[A-Z_]+:|\Z)")
    prep_time = _extract(r"PREP_TIME:\s*(.+)")
    cooking_time = _extract(r"COOKING_TIME:\s*(.+)")
    calories = _extract(r"CALORIES:\s*(.+)")
    protein = _extract(r"PROTEIN:\s*(.+)")
    carbs = _extract(r"CARBS:\s*(.+)")
    fat = _extract(r"FAT:\s*(.+)")
    ingredients = _extract(r"INGREDIENTS:\s*(.+?)(?=\nINSTRUCTIONS:|\Z)")
    instructions = _extract(r"INSTRUCTIONS:\s*(.+?)(?=\nCOOKING_TIPS:|\Z)")
    cooking_tips = _extract(r"COOKING_TIPS:\s*(.+?)(?=\nSTORAGE_TIPS:|\Z)")
    storage_tips = _extract(r"STORAGE_TIPS:\s*(.+?)(?=\nALTERNATIVE_INGREDIENTS:|\Z)")
    alternative_ingredients = _extract(
        r"ALTERNATIVE_INGREDIENTS:\s*(.+?)(?=\nSERVING_SUGGESTIONS:|\Z)"
    )
    serving_suggestions = _extract(r"SERVING_SUGGESTIONS:\s*(.+)")

    # Clean up the first line only for single-line fields (defensive against
    # stray extra content the model might append).
    def _first_line(value: str) -> str:
        return value.splitlines()[0].strip() if value else value

    def _get_emoji(value: str) -> str:
        line = value.replace("<", "").replace(">", "").strip()
        for token in line.split():
            if any(ord(c) > 127 for c in token):
                return token
        return line.split()[0] if line else "🍽️"

    return {
        "recipe_name": _first_line(recipe_name),
        "emoji": _get_emoji(dish_emoji_raw),
        "description": description,
        "prep_time": _first_line(prep_time),
        "cooking_time": _first_line(cooking_time),
        "calories": _first_line(calories),
        "protein": _first_line(protein),
        "carbs": _first_line(carbs),
        "fat": _first_line(fat),
        "ingredients": ingredients,
        "instructions": instructions,
        "cooking_tips": cooking_tips,
        "storage_tips": storage_tips,
        "alternative_ingredients": alternative_ingredients,
        "serving_suggestions": serving_suggestions,
    }


def _to_markdown(parsed: dict, raw_fallback: str) -> str:
    """Build a clean Markdown version of the recipe for download/export."""
    if not parsed.get("recipe_name"):
        return raw_fallback

    return f"""# {parsed['recipe_name']}

{parsed.get('description', '')}

**Prep Time:** {parsed.get('prep_time', '-')}  
**Cooking Time:** {parsed.get('cooking_time', '-')}  
**Calories:** {parsed.get('calories', '-')} | **Protein:** {parsed.get('protein', '-')} | **Carbs:** {parsed.get('carbs', '-')} | **Fat:** {parsed.get('fat', '-')}

## Ingredients
{parsed.get('ingredients', '')}

## Instructions
{parsed.get('instructions', '')}

## Cooking Tips
{parsed.get('cooking_tips', '')}

## Storage Tips
{parsed.get('storage_tips', '')}

## Alternative Ingredients
{parsed.get('alternative_ingredients', '')}

## Serving Suggestions
{parsed.get('serving_suggestions', '')}
"""
