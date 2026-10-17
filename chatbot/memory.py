"""In-memory per-session chat history for the MVP.

Important: this storage is process-local and is lost when the app restarts.
Replace it with Redis or a database-backed history store before production use.
"""

from langchain_core.chat_history import InMemoryChatMessageHistory

_history_store: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Return a history object dedicated to one conversation session."""
    if session_id not in _history_store:
        _history_store[session_id] = InMemoryChatMessageHistory()
    return _history_store[session_id]


def clear_session(session_id: str) -> None:
    """Clear a session's messages without touching other sessions."""
    history = _history_store.get(session_id)
    if history is not None:
        history.clear()
