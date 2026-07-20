"""
Database engine and session configuration (SQLite + SQLAlchemy ORM).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./recipes.db")

# check_same_thread=False is required for SQLite when used with FastAPI's
# threaded request handling.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Create all tables if they do not already exist."""
    from database import models  # noqa: F401 (ensures models are registered)
    Base.metadata.create_all(bind=engine)

    # Simple migration: add emoji column if missing
    try:
        with engine.begin() as conn:
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE recipes ADD COLUMN emoji VARCHAR(10);"))
    except Exception:
        pass  # Column already exists or table not ready


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
