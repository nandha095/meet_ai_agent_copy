import warnings

warnings.filterwarnings(
    "ignore",
    message="Scope has changed*"
)



from fastapi import FastAPI

from app.core.config import settings
from app.db.init_db import init_db

from app.api import emails, meeting, webhooks, replies, auth
from app.services.reply_worker import run_reply_worker

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
from app.api.outlook_auth import router as outlook_auth_router
from fastapi.staticfiles import StaticFiles
app: FastAPI = FastAPI()
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
from app.api import auth
app = FastAPI(
    title="AI Meeting Agent",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Routers
# --------------------
app.include_router(emails.router, prefix="/emails", tags=["Emails"])
app.include_router(meeting.router, prefix="/meetings", tags=["Meetings"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(replies.router, prefix="/replies", tags=["Replies"])
# app.include_router(auth.router)

#  ONLY THIS FOR GOOGLE AUTH
app.include_router(auth.router, tags=["Auth"])
app.include_router(outlook_auth_router)



# --------------------
# Scheduler
# --------------------
scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup_event():
    init_db()

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
@app.get("/")
def health_check():
    return {
        "status": "running",
        "env": settings.ENV
    }
