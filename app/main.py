from fastapi import FastAPI

from app.core.config import settings
from app.db.init_db import init_db

from app.api import emails, meeting, webhooks, google_auth, replies
from app.services.reply_worker import run_reply_worker

from apscheduler.schedulers.background import BackgroundScheduler


app = FastAPI(
    title="AI Meeting Agent",
    version="1.0.0"
)

# --------------------
# Routers
# --------------------
app.include_router(emails.router, prefix="/emails", tags=["Emails"])
app.include_router(meeting.router, prefix="/meetings", tags=["Meetings"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

app.include_router(google_auth.router, prefix="/auth/google", tags=["Google Auth"])
app.include_router(replies.router, prefix="/replies", tags=["Replies"])


# --------------------
# Scheduler
# --------------------
scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup_event():
    # 1️ Initialize DB
    init_db()

    # 2️ Start scheduler safely
    if not scheduler.running:
        scheduler.add_job(
            run_reply_worker,
            trigger="interval",
            minutes=1,
            # seconds=30,
            id="reply_worker",
            replace_existing=True
        )
        scheduler.start()
        print("⏱️ Background reply worker started (every 1 minutes)")


@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Background scheduler stopped")


# --------------------
# Health Check
# --------------------
@app.get("/")
def health_check():
    return {
        "status": "running",
        "env": settings.ENV
    }
