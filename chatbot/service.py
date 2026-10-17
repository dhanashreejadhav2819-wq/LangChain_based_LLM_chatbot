"""Application service: chain creation, multi-turn invocation, and error handling."""

import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

from .config import GROQ_API_KEY, MAX_QUESTION_CHARS
from .memory import get_session_history
from .model import create_model
from .prompts import build_prompt

logger = logging.getLogger(__name__)
_chat_chain: Runnable | None = None


class ChatbotError(RuntimeError):
    """Safe, user-facing chatbot error."""


def _get_chain() -> Runnable:
    """Create the chain once per process and reuse it for later messages."""
    global _chat_chain
    if _chat_chain is None:
        try:
            model = create_model()
            base_chain = build_prompt() | model
            _chat_chain = base_chain
        except Exception as exc:
            # Do not display provider configuration details or secrets to end users.
            logger.exception("Could not initialize the chatbot chain")
            if not GROQ_API_KEY:
                raise ChatbotError(
                    "Groq is not configured yet. Add GROQ_API_KEY to your local .env "
                    "file or Streamlit deployment secrets, then restart the app."
                ) from exc
            raise ChatbotError(
                "The chatbot is not configured correctly. Check the server's environment settings."
            ) from exc
    return _chat_chain


def ask(question: str, session_id: str) -> str:
    """Generate an answer while preserving this session's conversation history."""
    if not question or not question.strip():
        raise ChatbotError("Please enter a message before sending.")
    if len(question) > MAX_QUESTION_CHARS:
        raise ChatbotError(
            f"Your message is too long. Keep it under {MAX_QUESTION_CHARS:,} characters."
        )
    if not session_id or not session_id.strip():
        raise ChatbotError("The conversation session is invalid. Start a new chat.")

    try:
        history = get_session_history(session_id)
        response: Any = _get_chain().invoke(
            {"question": question.strip(), "history": history.messages}
        )
        content = response.content
        if isinstance(content, str):
            answer = content.strip()
        elif isinstance(content, list):
            answer = "".join(
                str(part.get("text", "")) if isinstance(part, dict) else str(part)
                for part in content
            ).strip()
        else:
            answer = str(content).strip()
        if not answer:
            raise ChatbotError("The AI service returned an empty response. Please try again.")
        history.add_messages(
            [HumanMessage(content=question.strip()), AIMessage(content=answer)]
        )
        return answer
    except ChatbotError:
        raise
    except Exception as exc:
        logger.exception("LLM request failed for session %s", session_id)
        raise ChatbotError(
            "I couldn't get a response from the AI service. Please try again in a moment."
        ) from exc
