import streamlit as st
from dotenv import load_dotenv

from UI.chatbot import render_chatbot_page
from UI.login import render_login_page

load_dotenv()


def main():
    st.set_page_config(
        page_title="Lumen Travel Assistant",
        page_icon="✈️",
        layout="centered",
    )

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.session_state.authenticated:
        render_chatbot_page()
    else:
        render_login_page()


if __name__ == "__main__":
    main()
