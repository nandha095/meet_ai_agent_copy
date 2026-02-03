import os
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from app.core.config import settings
from app.models.google_token import GoogleToken


SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",

    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
]


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

CLIENT_SECRET_FILE = os.path.join(BASE_DIR, "client_secret.json")


# -------------------------------------------------
# OAUTH FLOW (LOGIN)
# -------------------------------------------------
def get_google_auth_flow():
    return Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
       
    )


# -------------------------------------------------
# CREDENTIALS FOR API USAGE (Calendar / Gmail)
# -------------------------------------------------
def get_google_credentials(db, user_id: int) -> Credentials | None:
    """
    Returns refreshed Google credentials for a user
    """

    token = (
        db.query(GoogleToken)
        .filter(GoogleToken.user_id == user_id)
        .first()
    )

    if not token:
        return None

    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=token.scopes.split(","),
    )

    # 🔄 Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        token.access_token = creds.token
        token.expiry = creds.expiry
        token.updated_at = datetime.utcnow()

        db.commit()

    return creds
