import warnings
warnings.filterwarnings("ignore", message="Scope has changed*")

import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.init_db import init_db
from app.api import emails, meeting, webhooks, replies, auth
from app.api.outlook_auth import router as outlook_auth_router


app = FastAPI(
    title="AI Meeting Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Auth"])
app.include_router(outlook_auth_router)
app.include_router(emails.router, prefix="/emails", tags=["Emails"])
app.include_router(meeting.router, prefix="/meetings", tags=["Meetings"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(replies.router, prefix="/replies", tags=["Replies"])

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.on_event("startup")
def startup_event():
    init_db()
    print("API started")


@app.get("/health")
def health_check():
    return {
        "status": "running",
        "env": settings.ENV
    }
