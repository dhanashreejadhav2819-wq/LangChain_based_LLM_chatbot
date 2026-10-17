import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda

import chatbot.service as service
from chatbot.memory import clear_session, get_session_history
from chatbot.service import ChatbotError, ask


def test_service_preserves_multi_turn_context_without_duplicate_history(monkeypatch) -> None:
    session = "service-multi-turn"
    clear_session(session)
    observed = []

    def respond(payload):
        observed.append(payload.to_messages())
        return AIMessage(content=f"answer {len(observed)}")

    monkeypatch.setattr(service, "create_model", lambda: RunnableLambda(respond))
    monkeypatch.setattr(service, "_chat_chain", None)

    assert ask("My name is Asha", session) == "answer 1"
    assert ask("What is my name?", session) == "answer 2"
    assert len(observed[0]) == 2  # system instructions and first question
    assert [type(message) for message in observed[1][-3:-1]] == [HumanMessage, AIMessage]
    assert observed[1][-1].content == "What is my name?"
    assert len(get_session_history(session).messages) == 4


def test_empty_and_oversized_inputs_are_rejected(monkeypatch) -> None:
    monkeypatch.setattr(service, "MAX_QUESTION_CHARS", 3)
    with pytest.raises(ChatbotError, match="enter a message"):
        ask("  ", "input-validation")
    with pytest.raises(ChatbotError, match="too long"):
        ask("four", "input-validation")


def test_model_failure_does_not_add_fabricated_assistant_message(monkeypatch) -> None:
    session = "service-failure"
    clear_session(session)

    def fail(_payload):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(service, "create_model", lambda: RunnableLambda(fail))
    monkeypatch.setattr(service, "_chat_chain", None)
    with pytest.raises(ChatbotError, match="couldn't get a response"):
        ask("hello", session)
    assert get_session_history(session).messages == []
