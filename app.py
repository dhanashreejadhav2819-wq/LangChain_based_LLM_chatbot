"""Streamlit UI for ConvoCore."""

import hmac
import logging
import os
import uuid

import streamlit as st

st.set_page_config(page_title="ConvoCore", page_icon="💬", layout="centered")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Streamlit Community Cloud stores deployment secrets in st.secrets. Load them
# into the environment before importing modules that read configuration.
for _key in (
    "GROQ_API_KEY",
    "GROQ_MODEL",
    "TEMPERATURE",
    "MAX_TOKENS",
    "REQUEST_TIMEOUT_SECONDS",
    "MAX_QUESTION_CHARS",
    "APP_ACCESS_PASSWORD",
):
    if _key not in os.environ:
        try:
            _value = st.secrets.get(_key)
            if _value is not None:
                os.environ[_key] = str(_value)
        except Exception:
            # st.secrets may not exist during local development; .env is used there.
            pass

from chatbot.config import APP_ACCESS_PASSWORD  # noqa: E402
from chatbot.memory import clear_session  # noqa: E402
from chatbot.service import ChatbotError, ask  # noqa: E402

if "authenticated" not in st.session_state:
    st.session_state.authenticated = not bool(APP_ACCESS_PASSWORD)

if APP_ACCESS_PASSWORD and not st.session_state.authenticated:
    st.title("💬 ConvoCore")
    st.caption("Enter the application password to continue.")
    with st.form("access_form"):
        password = st.text_input("Application password", type="password")
        submitted = st.form_submit_button("Unlock")
    if submitted:
        if hmac.compare_digest(password.encode("utf-8"), APP_ACCESS_PASSWORD.encode("utf-8")):
            st.session_state.authenticated = True
            st.rerun()
        st.error("That password is incorrect.")
    st.stop()

if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 ConvoCore")
st.caption("A LangChain-powered chatbot with a system prompt and multi-turn memory.")

with st.sidebar:
    st.subheader("Conversation")
    st.caption("Each chat has a separate session ID.")

    if st.button("＋ New conversation", use_container_width=True):
        clear_session(st.session_state.session_id)
        st.session_state.session_id = uuid.uuid4().hex
        st.session_state.messages = []
        st.rerun()

    if st.button("Clear current conversation", use_container_width=True):
        clear_session(st.session_state.session_id)
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Conversation history is held in server memory and cleared when the app restarts.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask a question or continue the conversation...")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask(user_input, st.session_state.session_id)
                st.markdown(answer)
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except ChatbotError as exc:
                st.error(str(exc))
            except Exception:
                logger.exception("Unexpected error while handling a chat request")
                st.error("Something went wrong. Please try again.")
