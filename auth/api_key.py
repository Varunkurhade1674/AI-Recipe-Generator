"""
API key verification for multiple providers.

The key is never persisted anywhere (no DB, no .env, no logs). It is only
ever handed back to the caller so it can be placed in the signed session
cookie for the duration of the browser session.
"""

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

def verify_api_key(provider: str, api_key: str) -> tuple[bool, str]:
    """
    Perform a lightweight live request against the selected provider to confirm 
    the API key is valid and usable.

    Returns:
        (is_valid, message)
    """
    if not api_key or not api_key.strip():
        return False, "API key cannot be empty."

    api_key = api_key.strip()

    try:
        if provider == "Groq":
            llm = ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile", max_tokens=5, timeout=15)
        elif provider == "OpenAI":
            llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", max_tokens=5, request_timeout=15)
        elif provider == "Anthropic":
            llm = ChatAnthropic(api_key=api_key, model="claude-3-haiku-20240307", max_tokens=5, default_request_timeout=15)
        elif provider == "Gemini":
            llm = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-1.5-flash", max_output_tokens=5, timeout=15)
        elif provider == "OpenRouter":
            llm = ChatOpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                model="meta-llama/llama-3.3-70b-instruct",
                max_tokens=5,
                request_timeout=15
            )
        else:
            return False, "Unknown provider."

        # A minimal, cheap call just to confirm the key + model are usable.
        llm.invoke("ping")
        return True, f"Connected to {provider}"
    except Exception as exc:  # noqa: BLE001
        error_text = str(exc).lower()
        if "401" in error_text or "invalid" in error_text or "unauthorized" in error_text or "permission_denied" in error_text:
            return False, "Invalid API Key"
        return False, f"Could not verify API key: {exc}"
