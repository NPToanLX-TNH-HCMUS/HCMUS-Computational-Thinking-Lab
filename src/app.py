import os

import streamlit as st
from dotenv import load_dotenv

from RAG.rag import RAG
from utils.call_llm import OllamaServerError

load_dotenv()
PINGGY_URL = os.getenv("PINGGY_URL", "").rstrip("/")


def render_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main():
    st.set_page_config(
        page_title="Lumen Travel Assistant",
        page_icon="✈️",
        layout="centered",
    )

    st.title("✈️ Lumen Travel Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not PINGGY_URL:
        st.error(
            "PINGGY_URL is not configured. "
            "Please add the Ollama Server URL to the .env file."
        )
        st.stop()

    render_chat_history()

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
                answer = RAG(PINGGY_URL).pipelining(question)
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


if __name__ == "__main__":
    main()
