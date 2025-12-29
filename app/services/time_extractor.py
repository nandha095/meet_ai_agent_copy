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
from datetime import datetime
import pytz
import re

# TZ_MAP = {
#     "EST": "America/New_York",
#     "EDT": "America/New_York",
#     "PST": "America/Los_Angeles",
#     "PDT": "America/Los_Angeles",
#     "IST": "Asia/Kolkata",
#     "UTC": "UTC",
#     "GMT": "UTC",
# }

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
}

def extract_time_and_timezone(text: str):
    try:
        # 1️ Parse datetime WITHOUT timezone
        naive_dt = parser.parse(text, fuzzy=True, ignoretz=True)
    except Exception:
        return None

    # 2️ Extract timezone abbreviation manually
    tz_match = re.search(r"\b(EST|EDT|PST|PDT|IST|UTC|GMT)\b", text, re.IGNORECASE)
    if not tz_match:
        return None

    tz_abbr = tz_match.group(1).upper()
    tz_name = TZ_MAP.get(tz_abbr)
    if not tz_name:
        return None

    client_tz = pytz.timezone(tz_name)
    ist_tz = pytz.timezone("Asia/Kolkata")

    # 3️ Proper localization (THIS IS THE FIX)
    client_dt = client_tz.localize(naive_dt)

    # 4️ Correct timezone conversion
    ist_dt = client_dt.astimezone(ist_tz)

    return {
        "client_datetime": client_dt,
        "ist_datetime": ist_dt,
        "client_timezone": tz_name
    }
