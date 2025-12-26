from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.services.gmail_auth import get_google_auth_flow

router = APIRouter()

@router.get("/login")
def google_login():
    flow = get_google_auth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )
    return RedirectResponse(auth_url)

@router.get("/callback")
def google_callback(code: str):
    flow = get_google_auth_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    with open("gmail_token.json", "w") as f:
        f.write(creds.to_json())

    return {"message": "Gmail connected successfully"}
