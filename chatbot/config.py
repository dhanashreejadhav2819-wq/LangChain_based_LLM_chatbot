"""Validated application configuration loaded from env or Streamlit secrets."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(override=False)


class ConfigurationError(ValueError):
    """Raised when an application setting is invalid."""


@dataclass(frozen=True)
class Settings:
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    temperature: float = 0.3
    max_tokens: int = 700
    request_timeout_seconds: float = 30.0
    max_question_chars: int = 8000
    app_access_password: str = ""


def load_settings(environ: dict[str, str] | None = None) -> Settings:
    """Load and validate settings; passing a mapping makes this independently testable."""
    values = os.environ if environ is None else environ
    try:
        settings = Settings(
            groq_api_key=values.get("GROQ_API_KEY", "").strip(),
            groq_model=values.get("GROQ_MODEL", "openai/gpt-oss-20b").strip(),
            temperature=float(values.get("TEMPERATURE", "0.3")),
            max_tokens=int(values.get("MAX_TOKENS", "700")),
            request_timeout_seconds=float(values.get("REQUEST_TIMEOUT_SECONDS", "30")),
            max_question_chars=int(values.get("MAX_QUESTION_CHARS", "8000")),
            app_access_password=values.get("APP_ACCESS_PASSWORD", ""),
        )
    except (TypeError, ValueError) as exc:
        raise ConfigurationError("Numeric configuration values must be valid numbers.") from exc

    if not settings.groq_model:
        raise ConfigurationError("GROQ_MODEL must not be empty.")
    if not 0 <= settings.temperature <= 2:
        raise ConfigurationError("TEMPERATURE must be between 0 and 2.")
    if settings.max_tokens < 1:
        raise ConfigurationError("MAX_TOKENS must be greater than zero.")
    if settings.request_timeout_seconds <= 0:
        raise ConfigurationError("REQUEST_TIMEOUT_SECONDS must be greater than zero.")
    if settings.max_question_chars < 1:
        raise ConfigurationError("MAX_QUESTION_CHARS must be greater than zero.")
    return settings


SETTINGS = load_settings()
GROQ_API_KEY = SETTINGS.groq_api_key
GROQ_MODEL = SETTINGS.groq_model
TEMPERATURE = SETTINGS.temperature
MAX_TOKENS = SETTINGS.max_tokens
REQUEST_TIMEOUT_SECONDS = SETTINGS.request_timeout_seconds
MAX_QUESTION_CHARS = SETTINGS.max_question_chars
APP_ACCESS_PASSWORD = SETTINGS.app_access_password
