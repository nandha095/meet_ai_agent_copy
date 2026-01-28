from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.db.session import get_db
from app.models.user import User
from app.models.google_token import GoogleToken
from app.services.gmail_auth import get_google_auth_flow
# from app.services.email_service import send_system_email
from app.services.email_service import send_system_email
from app.core.config import settings
from jose import jwt
from app.models.outlook_token import OutlookToken
from fastapi.responses import RedirectResponse
from googleapiclient.discovery import build
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from app.api.schemas import ForgotPasswordRequest, ResetPasswordRequest

SECRET_KEY = settings.JWT_SECRET_KEY
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not GOOGLE_CLIENT_ID:
    raise RuntimeError("GOOGLE_CLIENT_ID not set in environment")





# --------------------
# CONFIG
# --------------------
# SECRET_KEY = "CHANGE_THIS_SECRET_LATER"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
RESET_TOKEN_EXPIRE_MINUTES = 15


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --------------------
# PASSWORD HELPERS
# --------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# --------------------
# JWT HELPERS
# --------------------
def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user_id = int(user_id)

    except ExpiredSignatureError:
        # THIS is the key fix
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

def create_password_reset_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# =========================================================
# USER REGISTER
# =========================================================
@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):

    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password too long (max 72 bytes)"
        )

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}

# =========================================================
# USER LOGIN (FIXED )
# =========================================================
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# Google OAuth login endpoint to connect Google account
@router.get("/google/login")
def google_login():
    flow = get_google_auth_flow()

    auth_url, _ = flow.authorization_url(
    access_type="offline",
    prompt="consent",
    include_granted_scopes="true"
)


    return RedirectResponse(auth_url)



@router.get("/google/callback")
def google_callback(
    code: str,
    db: Session = Depends(get_db)
):
    print("🔥 GOOGLE CALLBACK HIT")

    flow = get_google_auth_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    if not creds.id_token:
        raise HTTPException(
            status_code=400,
            detail="No ID token received from Google"
        )

    from google.oauth2 import id_token
    from google.auth.transport import requests

    idinfo = id_token.verify_oauth2_token(
        creds.id_token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )

    google_email = idinfo.get("email")

    if not google_email:
        raise HTTPException(
            status_code=400,
            detail="Unable to fetch Google email"
        )

    user = db.query(User).filter(User.email == google_email).first()
    if not user:
        raise HTTPException(
            status_code=403,
            detail="Please login before connecting Google"
        )

    db.query(GoogleToken).filter(
        GoogleToken.user_id == user.id
    ).delete(synchronize_session=False)
    db.commit()

    token = GoogleToken(
        user_id=user.id,
        access_token=creds.token,
        refresh_token=creds.refresh_token,
        token_uri=creds.token_uri,
        scopes=" ".join(creds.scopes),
        expiry=creds.expiry
    )

    db.add(token)
    db.commit()

    return RedirectResponse(
    url="http://127.0.0.1:5500/frontend/dashboard.html"
)

# google connection status endpoint
@router.get("/google/status")
def google_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    token = db.query(GoogleToken).filter(
        GoogleToken.user_id == current_user.id
    ).first()

    return {
        "connected": bool(token)
    }

# outlook connection status endpoint
@router.get("/outlook/status")
def outlook_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    token = db.query(OutlookToken).filter(
        OutlookToken.user_id == current_user.id
    ).first()

    return {"connected": bool(token)}

# google disconnect endpoint
@router.post("/google/disconnect")
def disconnect_google(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    token = db.query(GoogleToken).filter(
        GoogleToken.user_id == current_user.id
    ).first()

    if token:
        db.delete(token)
        db.commit()

    return {"disconnected": True}

# outlook disconnect endpoint
@router.post("/outlook/disconnect")
def disconnect_outlook(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    token = db.query(OutlookToken).filter(
        OutlookToken.user_id == current_user.id
    ).first()

    if token:
        db.delete(token)
        db.commit()

    return {"disconnected": True}



# forgot password endpoints
@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()

    # Do NOT reveal if user exists
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}

    token = create_password_reset_token(user.id)

    reset_link = f"http://127.0.0.1:5500/frontend/reset-password.html?token={token}"


    send_system_email(
        to_email=user.email,
        subject="Reset your password",
        body_text=f"Reset your password using this link:\n{reset_link}",
        body_html=f"""
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Password</a>
        """
    )

    return {"message": "If the email exists, a reset link has been sent"}


# reset password endpoint
@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            request.token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if len(request.new_password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password too long")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(request.new_password)
    db.commit()

    return {"message": "Password reset successful"}