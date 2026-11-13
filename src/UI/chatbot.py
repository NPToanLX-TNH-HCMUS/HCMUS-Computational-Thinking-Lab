import os

import streamlit as st

from RAG.rag import RAG
from utils.call_llm import OllamaServerError


def _render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _sign_out() -> None:
    st.session_state.authenticated = False
    st.session_state.pop("user", None)
    st.session_state.messages = []
    st.rerun()


def render_chatbot_page() -> None:
    user = st.session_state.get("user", {})
    pinggy_url = os.getenv("PINGGY_URL", "").rstrip("/")

    with st.sidebar:
        st.write(f"Signed in as: {user.get('email', 'user')}")
        if st.button("Sign out", use_container_width=True):
            _sign_out()

    st.title("✈️ Lumen Travel Assistant")
    st.caption("Ask questions based only on the team's travel guide.")

    if not pinggy_url:
        st.error(
            "PINGGY_URL is not configured. "
            "Please add the Ollama Server URL to the .env file."
        )
        return

    _render_chat_history()

    question = st.chat_input("Ask a question about a travel destination...")
    if not question or not question.strip():
        return

    question = question.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the travel guide and generating an answer..."):
            try:
                answer = RAG(pinggy_url).pipelining(question)
            except OllamaServerError as error:
                st.error(str(error))
                answer = None
            except Exception:
                st.error(
                    "The application could not process your question. "
                    "Please check the configuration and try again."
                )
                answer = None

        if answer:
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
