import os

import requests


class FirebaseAuthError(Exception):
    """Raise when Firebase Authentication cannot complete a request."""


def _auth_request(endpoint: str, email: str, password: str) -> dict:
    api_key = os.getenv("FIREBASE_API_KEY", "").strip()
    if not api_key:
        raise FirebaseAuthError(
            "FIREBASE_API_KEY is not configured. Please update the .env file."
        )

    try:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}",
            params={"key": api_key},
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as error:
        try:
            message = response.json()["error"]["message"]
        except (KeyError, ValueError):
            message = "Firebase returned an authentication error."
        raise FirebaseAuthError(_friendly_error(message)) from error
    except requests.RequestException as error:
        raise FirebaseAuthError(
            "Unable to connect to Firebase Authentication. Please try again."
        ) from error


def _friendly_error(message: str) -> str:
    messages = {
        "EMAIL_EXISTS": "This email address is already registered.",
        "EMAIL_NOT_FOUND": "No account was found with this email address.",
        "INVALID_PASSWORD": "The password is incorrect.",
        "INVALID_EMAIL": "The email address is invalid.",
        "WEAK_PASSWORD": "The password must contain at least 6 characters.",
        "USER_DISABLED": "This account has been disabled.",
    }
    return messages.get(message, f"Firebase authentication failed: {message}.")


def sign_in(email: str, password: str) -> dict:
    return _auth_request("signInWithPassword", email, password)


def sign_up(email: str, password: str) -> dict:
    return _auth_request("signUp", email, password)
