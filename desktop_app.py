import sys
import os
import threading
import webbrowser
import time
import uvicorn

def start_api():
    # IMPORTANT: add bundled path to PYTHONPATH
    if hasattr(sys, "_MEIPASS"):
        sys.path.insert(0, sys._MEIPASS)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    t = threading.Thread(target=start_api, daemon=True)
    t.start()

    time.sleep(3)
    webbrowser.open("http://127.0.0.1:8000")
    t.join()
