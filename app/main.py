import warnings
warnings.filterwarnings("ignore", message="Scope has changed*")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.init_db import init_db

from app.api import emails, meeting, webhooks, replies, auth
from app.api.outlook_auth import router as outlook_auth_router

import sys
import os
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.reply_worker import run_reply_worker


scheduler = BackgroundScheduler()


app = FastAPI(
    title="AI Meeting Agent",
    version="1.0.0"
)

# --------------------
# Middleware
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Routers
# --------------------
app.include_router(auth.router, tags=["Auth"])
app.include_router(outlook_auth_router)

app.include_router(emails.router, prefix="/emails", tags=["Emails"])
app.include_router(meeting.router, prefix="/meetings", tags=["Meetings"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(replies.router, prefix="/replies", tags=["Replies"])

if getattr(sys, "frozen", False):
    # Running as EXE
    BASE_DIR = sys._MEIPASS
else:
    # Running normally (uvicorn)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# --------------------
# Frontend (optional)
# --------------------


# --------------------
# Startup
# --------------------
@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ API started")

    if not scheduler.running:
        scheduler.add_job(
            run_reply_worker,
            trigger="interval",
            minutes=1,
            id="reply_worker",
            replace_existing=True
        )
        scheduler.start()
        print("⏱️ Background reply worker started (every 1 minute)")


@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Background scheduler stopped")


# --------------------
# Health Check
# --------------------
@app.get("/health")
def health_check():
    return {
        "status": "running",
        "env": settings.ENV
    }
