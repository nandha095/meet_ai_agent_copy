# from dateutil import parser
# import pytz
# from datetime import datetime

# TZINFOS = {
#     "EST": pytz.timezone("America/New_York"),
#     "EDT": pytz.timezone("America/New_York"),
#     "PST": pytz.timezone("America/Los_Angeles"),
#     "IST": pytz.timezone("Asia/Kolkata"),
#     "UTC": pytz.UTC,
#     "GMT": pytz.UTC,
# }

# def extract_time_and_timezone(text: str):
#     try:
#         client_dt = parser.parse(
#             text,
#             fuzzy=True,
#             tzinfos=TZINFOS
#         )
#     except Exception:
#         return None

#     if not client_dt.tzinfo:
#         return None

#     ist_dt = client_dt.astimezone(pytz.timezone("Asia/Kolkata"))

#     return {
#         "client_datetime": client_dt,
#         "ist_datetime": ist_dt,
#         "client_timezone": str(client_dt.tzinfo)
#     }


from dateutil import parser
from datetime import datetime, timedelta
import pytz
import re

TZ_MAP = {
    "EST": "America/New_York",
    "EDT": "America/New_York",
    "CST": "America/Chicago",
    "CDT": "America/Chicago",
    "MST": "America/Denver",
    "MDT": "America/Denver",
    "PST": "America/Los_Angeles",
    "PDT": "America/Los_Angeles",
    "IST": "Asia/Kolkata",
    "UTC": "UTC",
    "GMT": "UTC",
    "BST": "Europe/London",

}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

def extract_time_and_timezone(text: str):
    try:
        # Normalize common typos and time formats
        text = re.sub(r"\btommorow\b", "tomorrow", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(\d{1,2})\.(\d{2})\s*(am|pm)\b", r"\1:\2 \3", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(\d{1,2})\.(\d{2})\b", r"\1:\2", text)

        # 1️ Parse datetime WITHOUT timezone
        naive_dt = parser.parse(text, fuzzy=True, ignoretz=True)
    except Exception:
        return None

    # 2️ Extract timezone (IANA name or abbreviation)
    tz_name = None
    iana_match = re.search(r"\b([A-Za-z]+/[A-Za-z_]+)\b", text)
    if iana_match:
        candidate = iana_match.group(1)
        try:
            pytz.timezone(candidate)
            tz_name = candidate
        except Exception:
            tz_name = None

    if not tz_name:
        tz_match = re.search(r"\b(EST|EDT|CST|CDT|MST|MDT|PST|PDT|IST|UTC|GMT|BST)\b", text, re.IGNORECASE)
        if not tz_match:
            return None
        tz_abbr = tz_match.group(1).upper()
        tz_name = TZ_MAP.get(tz_abbr)
        if not tz_name:
            return None

    client_tz = pytz.timezone(tz_name)
    ist_tz = pytz.timezone("Asia/Kolkata")

    # 3️ Handle relative days like "today", "tomorrow", "day after tomorrow"
    lower = text.lower()
    offset_days = 0
    if "day after tomorrow" in lower:
        offset_days = 2
    elif "tomorrow" in lower:
        offset_days = 1
    elif "today" in lower:
        offset_days = 0

    if offset_days:
        base_date = datetime.now(client_tz).date()
        if naive_dt.date() == base_date:
            naive_dt = naive_dt + timedelta(days=offset_days)

    # 3.5️ Handle weekdays like "next Monday" / "this Tuesday" / "Monday"
    weekday_match = re.search(
        r"\b(this|next)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        lower
    )
    if weekday_match:
        modifier = weekday_match.group(1) or ""
        weekday_name = weekday_match.group(2)

        next_week = "next week" in lower
        if next_week and modifier == "":
            modifier = "next"
        target_wd = WEEKDAYS[weekday_name]
        today_local = datetime.now(client_tz)
        current_wd = today_local.weekday()
        days_ahead = (target_wd - current_wd) % 7

        if modifier == "next":
            if next_week:
                # "next week <weekday>" = same weekday in next week
                days_ahead = days_ahead + 7 if days_ahead != 0 else 7
            else:
                # "next <weekday>" = next occurrence; if today, move to next week
                days_ahead = 7 if days_ahead == 0 else days_ahead
        elif modifier == "this":
            # if same day and time already passed, move to next week
            if days_ahead == 0 and naive_dt.time() <= today_local.time():
                days_ahead = 7
        else:
            # no modifier: if same day and time already passed, move to next week
            if days_ahead == 0 and naive_dt.time() <= today_local.time():
                days_ahead = 7

        base_date = today_local.date()
        naive_dt = datetime.combine(base_date, naive_dt.time()) + timedelta(days=days_ahead)

    # 4️ Proper localization (THIS IS THE FIX)
    client_dt = client_tz.localize(naive_dt)

    # 5️ Correct timezone conversion
    ist_dt = client_dt.astimezone(ist_tz)

    return {
        "client_datetime": client_dt,
        "ist_datetime": ist_dt,
        "client_timezone": tz_name,
        "timezone": tz_name,
    }
