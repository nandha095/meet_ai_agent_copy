from google_auth_oauthlib.flow import Flow
from fastapi import APIRouter

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar"
]

def get_google_auth_flow():
    return Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/auth/google/callback"
    )


