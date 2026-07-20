# 🍳 AI Recipe Generator

A production-ready, full-stack AI Recipe Generator built to learn **LangChain fundamentals**. Users bring their own Groq API key — nothing is ever hardcoded or stored on disk.

---

## Overview

Enter your ingredients, cuisine, meal type, diet preference, difficulty, and available cooking time — the app uses a LangChain **LCEL** pipeline (`PromptTemplate | ChatGroq | StrOutputParser`) running Llama 3.3 on Groq to generate a complete, structured recipe: description, ingredients, step-by-step instructions, estimated nutrition, cooking tips, storage tips, substitutions, and serving suggestions.

Every recipe you save is persisted to a local SQLite database via SQLAlchemy, viewable in a Recipe History tab, and exportable as Markdown.

---

## Features

- 🔐 Bring-your-own API key (Supports Groq, OpenAI, Anthropic, and Google Gemini), verified live before access is granted
- 🧠 LangChain LCEL chain: `PromptTemplate → ChatModel → StrOutputParser`
- 📝 Structured recipe output: name, description, ingredients, instructions, nutrition, tips, substitutions, serving suggestions
- 💾 Auto-saving to local SQLite persistence via SQLAlchemy ORM
- 📖 Recipe History with reopen support
- 📋 Copy to clipboard, ⬇️ Download as Markdown
- 🎨 Premium, responsive SaaS-style UI — pure HTML/CSS/JS, no frontend framework
- 🌮 Dynamic Cuisine Stickers — background emojis match the cuisine you select!
- 📺 YouTube Integration — instantly search for video tutorials of the generated recipe
- 🔔 Toast notifications, loading spinners, smooth animations

---

## Folder Structure

```
AI-Recipe-Generator/
├── auth/
│   ├── api_key.py        # Live Provider API key verification
│   └── session.py        # Server-signed session helpers (never persists the key)
├── database/
│   ├── database.py       # SQLAlchemy engine/session setup
│   └── models.py         # Recipe ORM model
├── chains/
│   ├── prompt.py         # LangChain PromptTemplate
│   └── recipe_chain.py   # LCEL chain: PromptTemplate | ChatModel | StrOutputParser
├── templates/
│   ├── login.html        # API key verification page
│   └── index.html        # Dashboard (generate + history)
├── static/
│   ├── style.css
│   └── script.js
├── app.py                # FastAPI entrypoint
├── requirements.txt
├── .env.example
└── README.md
```

> **Note:** the folder is named `chains/` rather than `langchain/` on purpose — naming a local package `langchain` would shadow the real `langchain` library on the Python import path and break every `import langchain...` statement in the project.

---

## Installation

```bash
git clone <this-repo>
cd AI-Recipe-Generator

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Database Setup

No manual setup needed. On first run, `app.py` calls `init_db()` on startup, which creates `recipes.db` (SQLite) and the `recipes` table automatically via SQLAlchemy's `Base.metadata.create_all()`.

## Running the Project

```bash
uvicorn app:app --reload
```

Then open **http://127.0.0.1:8000** in your browser.

## Usage Flow

1. Open the app — you'll land on the API key verification page.
2. Select your provider (Groq, OpenAI, Anthropic, Gemini), paste your API key, click **Verify & Continue**.
3. On success you're redirected to the dashboard and see **🟢 Connected**.
4. Fill in ingredients + preferences, click **Generate Recipe**.
5. The recipe is automatically saved to your local database!
6. Copy or download the result as Markdown. Saved recipes appear under **Recipe History**.
7. Click **Logout** at any time to clear your session and API key immediately.

## LangChain Components Used

| Concept | Where | Purpose |
|---|---|---|
| `PromptTemplate` | `chains/prompt.py` | Reusable, parameterized recipe prompt |
| `ChatModels` | `chains/recipe_chain.py` | LLMs instantiated per-request with the user's session key |
| `RunnableSequence` (LCEL) | `chains/recipe_chain.py` | `prompt | llm | parser` pipeline built with the `|` operator |
| `StrOutputParser` | `chains/recipe_chain.py` | Extracts plain text from the `AIMessage` before custom section parsing |

## API Key Authentication

- The key is submitted once via the login form and verified with a minimal live request.
- On success, it is placed **only** in the signed, server-side session cookie (`itsdangerous` via Starlette's `SessionMiddleware`).
- It is **never** written to SQLite, `.env`, or any log file.
- Every `ChatModel` instance is built fresh, per request, using the key pulled from the current session.
- **Logout** clears the entire session immediately.

## Screenshots

_Add screenshots of the login page and dashboard here._

`docs/screenshot-login.png`
`docs/screenshot-dashboard.png`

## Future Improvements

- Export to PDF in addition to Markdown
- User accounts with persistent, per-user recipe history
- Ingredient-based recipe search across saved history
