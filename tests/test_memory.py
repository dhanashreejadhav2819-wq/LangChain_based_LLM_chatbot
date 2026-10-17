"""Fast, provider-independent tests for session isolation and clearing."""

from langchain_core.messages import AIMessage, HumanMessage

from chatbot.memory import clear_session, get_session_history


def test_sessions_have_separate_histories() -> None:
    first = get_session_history("session-a")
    second = get_session_history("session-b")
    first.clear()
    second.clear()

    first.add_messages([HumanMessage(content="Hello"), AIMessage(content="Hi")])

    assert len(first.messages) == 2
    assert len(second.messages) == 0


def test_clear_session_removes_messages_only_from_selected_session() -> None:
    first = get_session_history("session-clear-a")
    second = get_session_history("session-clear-b")
    first.add_messages([HumanMessage(content="A")])
    second.add_messages([HumanMessage(content="B")])

    clear_session("session-clear-a")

    assert len(first.messages) == 0
    assert len(second.messages) == 1
