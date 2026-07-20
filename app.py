"""
AI Recipe Generator - FastAPI entrypoint.

Wires together: session-based Groq API key auth, the LangChain LCEL
recipe chain, and SQLite persistence via SQLAlchemy.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from database.database import init_db, get_db
from database.models import Recipe
from auth.api_key import verify_api_key
from auth.session import (
    set_session_api_key,
    get_session_api_key,
    get_session_provider,
    is_connected,
    clear_session,
    require_session_api_key,
)
from chains.recipe_chain import generate_recipe

app = FastAPI(title="AI Recipe Generator")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "dev-secret-change-me"),
    session_cookie="recipe_gen_session",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup():
    init_db()


# --------------------------------------------------------------------------
# Auth / Login routes
# --------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    """Show the login / API key verification page, or the dashboard if
    already connected."""
    if is_connected(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": None}
    )


@app.post("/verify", response_class=HTMLResponse)
def verify_key(request: Request, provider: str = Form(...), api_key: str = Form(...)):
    """Verify the submitted API key and start a session if valid."""
    is_valid, message = verify_api_key(provider, api_key)

    if not is_valid:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": message}, status_code=401
        )

    set_session_api_key(request, provider, api_key)
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/logout")
def logout(request: Request):
    """Clear the session (and the in-memory API key with it)."""
    clear_session(request)
    return RedirectResponse(url="/", status_code=302)


# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_connected(request):
        return RedirectResponse(url="/", status_code=302)

    provider = get_session_provider(request)
    recipes = db.query(Recipe).order_by(Recipe.created_at.desc()).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "recipes": [r.to_dict() for r in recipes], "provider": provider},
    )


# --------------------------------------------------------------------------
# Recipe generation API
# --------------------------------------------------------------------------

@app.post("/api/generate-recipe")
def api_generate_recipe(
    request: Request,
    ingredients: str = Form(...),
    cuisine: str = Form(""),
    meal_type: str = Form(""),
    diet_preference: str = Form(""),
    difficulty: str = Form(""),
    cooking_time: str = Form(""),
    db: Session = Depends(get_db),
):
    provider, api_key = require_session_api_key(request)

    if not ingredients.strip():
        raise HTTPException(status_code=400, detail="Please provide at least one ingredient.")

    try:
        recipe_data = generate_recipe(
            provider,
            api_key,
            {
                "ingredients": ingredients,
                "cuisine": cuisine,
                "meal_type": meal_type,
                "diet_preference": diet_preference,
                "difficulty": difficulty,
                "cooking_time": cooking_time,
            },
        )
        
        recipe = Recipe(
            recipe_name=recipe_data.get("recipe_name", "Untitled Recipe"),
            emoji=recipe_data.get("emoji", "🍽️"),
            cuisine=recipe_data.get("cuisine"),
            meal_type=recipe_data.get("meal_type"),
            diet_preference=recipe_data.get("diet_preference"),
            difficulty=recipe_data.get("difficulty"),
            ingredients=recipe_data.get("ingredients", ""),
            instructions=recipe_data.get("instructions", ""),
            description=recipe_data.get("description"),
            prep_time=recipe_data.get("prep_time"),
            cooking_time=recipe_data.get("cooking_time"),
            calories=recipe_data.get("calories"),
            protein=recipe_data.get("protein"),
            carbs=recipe_data.get("carbs"),
            fat=recipe_data.get("fat"),
            cooking_tips=recipe_data.get("cooking_tips"),
            storage_tips=recipe_data.get("storage_tips"),
            alternative_ingredients=recipe_data.get("alternative_ingredients"),
            serving_suggestions=recipe_data.get("serving_suggestions"),
            raw_markdown=recipe_data.get("raw_markdown"),
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        recipe_data["id"] = recipe.id
        recipe_data["created_at"] = recipe.created_at.isoformat() if recipe.created_at else None

    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Recipe generation failed: {exc}")

    return JSONResponse(content=recipe_data)


@app.post("/api/save-recipe")
async def save_recipe(request: Request, db: Session = Depends(get_db)):
    if not is_connected(request):
        raise HTTPException(status_code=401, detail="Not connected.")

    payload = await request.json()

    recipe = Recipe(
        recipe_name=payload.get("recipe_name", "Untitled Recipe"),
        emoji=payload.get("emoji", "🍽️"),
        cuisine=payload.get("cuisine"),
        meal_type=payload.get("meal_type"),
        diet_preference=payload.get("diet_preference"),
        difficulty=payload.get("difficulty"),
        ingredients=payload.get("ingredients", ""),
        instructions=payload.get("instructions", ""),
        description=payload.get("description"),
        prep_time=payload.get("prep_time"),
        cooking_time=payload.get("cooking_time"),
        calories=payload.get("calories"),
        protein=payload.get("protein"),
        carbs=payload.get("carbs"),
        fat=payload.get("fat"),
        cooking_tips=payload.get("cooking_tips"),
        storage_tips=payload.get("storage_tips"),
        alternative_ingredients=payload.get("alternative_ingredients"),
        serving_suggestions=payload.get("serving_suggestions"),
        raw_markdown=payload.get("raw_markdown"),
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return JSONResponse(content={"success": True, "recipe": recipe.to_dict()})


@app.get("/api/recipe/{recipe_id}")
def get_recipe(recipe_id: int, request: Request, db: Session = Depends(get_db)):
    if not is_connected(request):
        raise HTTPException(status_code=401, detail="Not connected.")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return JSONResponse(content=recipe.to_dict())


@app.get("/api/recipe/{recipe_id}/download")
def download_recipe(recipe_id: int, request: Request, db: Session = Depends(get_db)):
    if not is_connected(request):
        raise HTTPException(status_code=401, detail="Not connected.")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    filename = "".join(c for c in recipe.recipe_name if c.isalnum() or c in (" ", "_", "-")).strip()
    filename = filename.replace(" ", "_") or "recipe"

    return PlainTextResponse(
        content=recipe.raw_markdown or "",
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}.md"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
