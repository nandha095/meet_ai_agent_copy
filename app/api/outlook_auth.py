import os
import uuid
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt

from app.db.session import get_db
from app.models.oauth_state import OAuthState
from app.models.outlook_token import OutlookToken
from app.models.user import User
from app.api.auth import SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix="/auth/outlook",
    tags=["Outlook"]
)

AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

SCOPES = [
    "openid",
    "profile",
    "email",
    "offline_access",
    "Mail.Read",
    "Mail.Send",
    "User.Read",
]

# =====================================================
# OUTLOOK LOGIN
# =====================================================
@router.get("/login")
def outlook_login(token: str, db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    state = str(uuid.uuid4())

    oauth_state = OAuthState(
        state=state,
        user_id=user_id,
        expires_at=OAuthState.expiry()
    )
    db.add(oauth_state)
    db.commit()

    params = {
        "client_id": os.getenv("OUTLOOK_CLIENT_ID"),
        "response_type": "code",
        "redirect_uri": os.getenv("OUTLOOK_REDIRECT_URI"),
        "response_mode": "query",
        "scope": " ".join(SCOPES),
        "state": state,

        # ✅ FIXED
        "prompt": "select_account",
    }

    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")

# =====================================================
# OUTLOOK CALLBACK
# =====================================================
@router.get("/callback")
def outlook_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    # 1️⃣ Resolve state → user_id
    oauth_state = (
        db.query(OAuthState)
        .filter(OAuthState.state == state)
        .first()
    )

    if not oauth_state:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    user = db.query(User).filter(User.id == oauth_state.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # 2️⃣ Exchange code for token
    token_res = requests.post(
        TOKEN_URL,
        data={
            "client_id": os.getenv("OUTLOOK_CLIENT_ID"),
            "client_secret": os.getenv("OUTLOOK_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.getenv("OUTLOOK_REDIRECT_URI"),
            "scope": " ".join(SCOPES),
        },
    ).json()

    if "access_token" not in token_res:
        raise HTTPException(status_code=400, detail=token_res)

    access_token = token_res["access_token"]

    # 3️⃣ Fetch Outlook profile
    profile = requests.get(
    "https://graph.microsoft.com/v1.0/me",
    headers={"Authorization": f"Bearer {access_token}"},
    ).json()

    print("🔎 OUTLOOK PROFILE:", profile)  # keep for now

    outlook_email = profile.get("mail")

    if not outlook_email:
        raise HTTPException(
            status_code=400,
            detail=(
                "This Microsoft account does not have an Outlook mailbox. "
                "Please sign in using an @outlook.com or @hotmail.com account."
            )
        )



    # 4️⃣ Save / update Outlook token
    token = (
        db.query(OutlookToken)
        .filter(OutlookToken.user_id == user.id)
        .first()
    )

    if not token:
        token = OutlookToken(user_id=user.id)
        db.add(token)

    token.access_token = access_token
    token.refresh_token = token_res.get("refresh_token")
    token.expires_at = datetime.utcnow() + timedelta(
        seconds=token_res["expires_in"]
    )

    # 5️⃣ Update user
    user.outlook_email = outlook_email
    user.email_provider = "outlook"

    # 6️⃣ Cleanup used state
    db.delete(oauth_state)

    db.commit()

    return RedirectResponse(
        url="http://127.0.0.1:5500/frontend/dashboard.html"
)
