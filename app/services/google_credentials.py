from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from app.models.google_token import GoogleToken
from app.core.config import settings


def get_google_credentials(db: Session, user_id: int) -> Credentials:
    token = db.query(GoogleToken).filter(
        GoogleToken.user_id == user_id
    ).first()

    if not token:
        raise Exception("Google token not found for user")

    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=settings.GOOGLE_CLIENT_ID,          #  REQUIRED
        client_secret=settings.GOOGLE_CLIENT_SECRET,  #  REQUIRED
        scopes=token.scopes.split()
    )

    return creds
