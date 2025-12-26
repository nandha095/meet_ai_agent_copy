from dateutil import parser
import pytz
from datetime import datetime

TZINFOS = {
    "EST": pytz.timezone("America/New_York"),
    "EDT": pytz.timezone("America/New_York"),
    "PST": pytz.timezone("America/Los_Angeles"),
    "IST": pytz.timezone("Asia/Kolkata"),
    "UTC": pytz.UTC,
    "GMT": pytz.UTC,
}

def extract_time_and_timezone(text: str):
    try:
        client_dt = parser.parse(
            text,
            fuzzy=True,
            tzinfos=TZINFOS
        )
    except Exception:
        return None

    if not client_dt.tzinfo:
        return None

    ist_dt = client_dt.astimezone(pytz.timezone("Asia/Kolkata"))

    return {
        "client_datetime": client_dt,
        "ist_datetime": ist_dt,
        "client_timezone": str(client_dt.tzinfo)
    }
