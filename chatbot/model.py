"""LLM provider construction, kept separate so the provider can be changed."""

from langchain_groq import ChatGroq

from .config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    MAX_TOKENS,
    REQUEST_TIMEOUT_SECONDS,
    TEMPERATURE,
)


def create_model() -> ChatGroq:
    """Construct the configured Groq chat model."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your local .env file or deployment secrets."
        )

    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=REQUEST_TIMEOUT_SECONDS,
        max_retries=2,
    )
