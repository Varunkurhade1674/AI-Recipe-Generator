"""
Session management helpers.

The verified Groq API key lives ONLY inside the server-signed session
cookie (via Starlette's SessionMiddleware) for the lifetime of the
browser session. It is never written to disk.
"""

from fastapi import Request, HTTPException, status

SESSION_KEY = "api_key"
SESSION_PROVIDER = "provider"
SESSION_CONNECTED_FLAG = "connected"


def set_session_api_key(request: Request, provider: str, api_key: str) -> None:
    """Store the verified provider and API key in the signed session cookie."""
    request.session[SESSION_PROVIDER] = provider
    request.session[SESSION_KEY] = api_key
    request.session[SESSION_CONNECTED_FLAG] = True


def get_session_api_key(request: Request) -> str | None:
    """Retrieve the API key from the session, if present."""
    return request.session.get(SESSION_KEY)


def get_session_provider(request: Request) -> str | None:
    """Retrieve the provider from the session, if present."""
    return request.session.get(SESSION_PROVIDER)


def is_connected(request: Request) -> bool:
    """Check whether the current session has a verified connection."""
    return bool(request.session.get(SESSION_CONNECTED_FLAG))


def clear_session(request: Request) -> None:
    """Log the user out by wiping the session entirely."""
    request.session.clear()


def require_session_api_key(request: Request) -> tuple[str, str]:
    """
    FastAPI dependency-style helper: returns (provider, api_key) or raises a 401
    if the user has not verified a key yet.
    """
    api_key = get_session_api_key(request)
    provider = get_session_provider(request)
    if not api_key or not provider:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not connected to any provider. Please verify your API key first.",
        )
    return provider, api_key
