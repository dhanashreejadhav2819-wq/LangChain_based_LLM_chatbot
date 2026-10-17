import pytest

from chatbot.config import ConfigurationError, load_settings
from chatbot.model import create_model


def test_settings_defaults_and_key_requirement_is_separate() -> None:
    settings = load_settings({})
    assert settings.groq_api_key == ""
    assert settings.groq_model == "openai/gpt-oss-20b"
    assert settings.temperature == 0.3
    assert settings.max_tokens == 700


@pytest.mark.parametrize("values", [
    {"TEMPERATURE": "3"},
    {"MAX_TOKENS": "0"},
    {"REQUEST_TIMEOUT_SECONDS": "-1"},
    {"MAX_QUESTION_CHARS": "x"},
])
def test_invalid_settings_are_rejected(values: dict[str, str]) -> None:
    with pytest.raises(ConfigurationError):
        load_settings(values)


def test_model_requires_api_key_without_displaying_a_secret(monkeypatch) -> None:
    import chatbot.model as model

    monkeypatch.setattr(model, "GROQ_API_KEY", "")
    with pytest.raises(RuntimeError, match="GROQ_API_KEY is missing"):
        create_model()
