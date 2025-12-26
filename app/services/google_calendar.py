from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None

    if not os.path.exists("calendar_token.json"):
        raise Exception("calendar_token.json not found")

    creds = Credentials.from_authorized_user_file(
        "calendar_token.json", SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("calendar", "v3", credentials=creds)
