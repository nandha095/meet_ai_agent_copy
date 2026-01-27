import os
import requests
from datetime import datetime, timedelta
from app.models.outlook_token import OutlookToken


TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"


def get_valid_outlook_access_token(db, user_id: int) -> str:
    token = db.query(OutlookToken).filter(
        OutlookToken.user_id == user_id
    ).first()

    if not token:
        raise Exception("Outlook not connected")

    #  If token still valid → use it
    if token.expires_at and token.expires_at > datetime.utcnow():
        return token.access_token

    #  Refresh token
    res = requests.post(
        TOKEN_URL,
        data={
            "client_id": os.getenv("OUTLOOK_CLIENT_ID"),
            "client_secret": os.getenv("OUTLOOK_CLIENT_SECRET"),
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "scope": "openid profile email offline_access Mail.Read Mail.Send User.Read",
        },
    ).json()

    if "access_token" not in res:
        raise Exception(f"Outlook refresh failed: {res}")

    token.access_token = res["access_token"]
    token.expires_at = datetime.utcnow() + timedelta(
        seconds=res["expires_in"]
    )

    db.commit()

    return token.access_token
