import os
import time
import json
import threading
import webbrowser
import uvicorn
from app.main import app

from apscheduler.schedulers.background import BackgroundScheduler
from pystray import Icon, Menu, MenuItem
from PIL import Image

from app.services.reply_processor import process_replies
from app.db.session import SessionLocal

APP_DIR = os.path.expanduser("~/AppData/Roaming/MeetingAgent")
SESSION_FILE = os.path.join(APP_DIR, "session.json")


def start_api():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")



def start_agent(user_id: int):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: process_replies(SessionLocal(), user_id),
        "interval",
        minutes=1
    )
    scheduler.start()
    print("✅ Agent running in background")


def open_ui(icon, item):
    webbrowser.open("http://127.0.0.1:8000")


def quit_app(icon, item):
    icon.stop()
    os._exit(0)


def create_tray():
    image = Image.new("RGB", (64, 64), "blue")

    menu = Menu(
        MenuItem("Open Agent", open_ui),
        MenuItem("Exit", quit_app)
    )

    tray = Icon("MeetingAgent", image, "AI Meeting Agent", menu)
    tray.run()


if __name__ == "__main__":
    # Start API
    threading.Thread(target=start_api, daemon=True).start()
    time.sleep(3)

    # Start Agent
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            session = json.load(f)
        start_agent(session["user_id"])
    else:
        print("❌ No session found. Please login once.")

    # Start tray (blocks)
    create_tray()
