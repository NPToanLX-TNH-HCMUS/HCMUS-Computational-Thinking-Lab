import streamlit as st

from firebase_client import FirebaseAuthError, sign_in, sign_up


def _save_authenticated_user(user_data: dict) -> None:
    st.session_state.authenticated = True
    st.session_state.user = {
        "email": user_data.get("email", ""),
        "local_id": user_data.get("localId", ""),
        "id_token": user_data.get("idToken", ""),
    }
    st.session_state.messages = []


def _validate_form(email: str, password: str) -> bool:
    if not email.strip() or not password:
        st.warning("Please enter both an email address and a password.")
        return False
    return True


def render_login_page() -> None:
    st.title("🔐 Lumen Travel Assistant")
    st.caption("Sign in to access the travel assistant.")

    sign_in_tab, sign_up_tab = st.tabs(["Sign in", "Sign up"])

    with sign_in_tab:
        with st.form("sign_in_form"):
            email = st.text_input("Email", key="sign_in_email")
            password = st.text_input(
                "Password", type="password", key="sign_in_password"
            )
            submitted = st.form_submit_button("Sign in", use_container_width=True)

        if submitted and _validate_form(email, password):
            try:
                user_data = sign_in(email.strip(), password)
                _save_authenticated_user(user_data)
                st.success("Signed in successfully.")
                st.rerun()
            except FirebaseAuthError as error:
                st.error(str(error))

    with sign_up_tab:
        with st.form("sign_up_form"):
            email = st.text_input("Email", key="sign_up_email")
            password = st.text_input(
                "Password", type="password", key="sign_up_password"
            )
            confirm_password = st.text_input(
                "Confirm password", type="password", key="confirm_password"
            )
            submitted = st.form_submit_button(
                "Create account", use_container_width=True
            )

        if submitted and _validate_form(email, password):
            if password != confirm_password:
                st.error("The passwords do not match.")
            else:
                try:
                    user_data = sign_up(email.strip(), password)
                    _save_authenticated_user(user_data)
                    st.success("Account created successfully.")
                    st.rerun()
                except FirebaseAuthError as error:
                    st.error(str(error))
