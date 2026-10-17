from chatbot.prompts import SYSTEM_PROMPT, build_prompt


def test_prompt_has_instructions_history_and_current_question() -> None:
    prompt = build_prompt()
    assert "helpful general-purpose" in SYSTEM_PROMPT
    assert "history" in prompt.input_variables
    assert "question" in prompt.input_variables
    messages = prompt.format_messages(history=[], question="What is Python?")
    assert messages[0].content == SYSTEM_PROMPT
    assert messages[-1].content == "What is Python?"
