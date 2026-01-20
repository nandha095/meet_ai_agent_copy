# from datetime import datetime, timedelta
# import pytz

# WEEKDAYS = {
#     "monday": 0,
#     "tuesday": 1,
#     "wednesday": 2,
#     "thursday": 3,
#     "friday": 4,
#     "saturday": 5,
#     "sunday": 6
# }

# def convert_client_time_to_ist(
#     time_str: str,
#     timezone: str,
#     date_str: str = None,
#     weekday: str = None,
#     modifier: str = None  # 👈 NEW ("this" / "next")
# ):
#     """
#     Converts client-provided time + timezone to IST datetime
#     """

#     client_tz = pytz.timezone(timezone)
#     ist_tz = pytz.timezone("Asia/Kolkata")
#     now_client = datetime.now(client_tz)

#     # 1️ Decide date
#     if date_str:
#         base_date = datetime.fromisoformat(date_str).date()
#     elif weekday:
#         target = WEEKDAYS[weekday.lower()]
#         days_ahead = (target - now_client.weekday()) % 7
#         days_ahead = 7 if days_ahead == 0 else days_ahead
#         base_date = (now_client + timedelta(days=days_ahead)).date()
#     else:
#         base_date = (now_client + timedelta(days=1)).date()

#     # 2️ Parse time
#     hour, minute = map(int, time_str.split(":"))

#     client_dt = client_tz.localize(datetime(
#         base_date.year,
#         base_date.month,
#         base_date.day,
#         hour,
#         minute
#     ))

#     ist_dt = client_dt.astimezone(ist_tz)

#     return client_dt, ist_dt

from datetime import datetime, timedelta
import pytz

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def convert_client_time_to_ist(
    time_str: str,
    timezone: str,
    weekday: str,
    modifier: str = None,
):
    client_tz = pytz.timezone(timezone)
    ist_tz = pytz.timezone("Asia/Kolkata")

    now_client = datetime.now(client_tz)
    today_weekday = now_client.weekday()
    target_weekday = WEEKDAYS[weekday.lower()]

    days_ahead = (target_weekday - today_weekday) % 7

    if days_ahead == 0:
        days_ahead = 7

    if modifier == "next":
        days_ahead += 7

    meeting_date = (now_client + timedelta(days=days_ahead)).date()

    hour, minute = map(int, time_str.split(":"))

    client_dt = client_tz.localize(
        datetime(
            meeting_date.year,
            meeting_date.month,
            meeting_date.day,
            hour,
            minute,
        )
    )

    ist_dt = client_dt.astimezone(ist_tz)

    return client_dt, ist_dt


def convert_calendar_relative_to_ist(
    time_str: str,
    timezone: str,
    calendar_relative: str,
):
    client_tz = pytz.timezone(timezone)
    ist_tz = pytz.timezone("Asia/Kolkata")

    now_client = datetime.now(client_tz)

    # ✅ normalize parameter INSIDE function
    calendar_relative = calendar_relative.lower().strip()

    if calendar_relative == "today":
        base_date = now_client.date()

    elif calendar_relative == "tomorrow":
        base_date = (now_client + timedelta(days=1)).date()

    else:
        raise ValueError(f"Unsupported calendar_relative value: {calendar_relative}")

    hour, minute = map(int, time_str.split(":"))

    client_dt = client_tz.localize(
        datetime(
            base_date.year,
            base_date.month,
            base_date.day,
            hour,
            minute,
        )
    )

    ist_dt = client_dt.astimezone(ist_tz)

    return client_dt, ist_dt
