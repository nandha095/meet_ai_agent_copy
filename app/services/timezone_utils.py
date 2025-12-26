from datetime import datetime, timedelta
import pytz

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}

def convert_client_time_to_ist(
    time_str: str,
    timezone: str,
    date_str: str = None,
    weekday: str = None
):
    """
    Converts client-provided time + timezone to IST datetime
    """

    client_tz = pytz.timezone(timezone)
    ist_tz = pytz.timezone("Asia/Kolkata")
    now_client = datetime.now(client_tz)

    # 1️⃣ Decide date
    if date_str:
        base_date = datetime.fromisoformat(date_str).date()
    elif weekday:
        target = WEEKDAYS[weekday.lower()]
        days_ahead = (target - now_client.weekday()) % 7
        days_ahead = 7 if days_ahead == 0 else days_ahead
        base_date = (now_client + timedelta(days=days_ahead)).date()
    else:
        base_date = (now_client + timedelta(days=1)).date()

    # 2️⃣ Parse time
    hour, minute = map(int, time_str.split(":"))

    client_dt = client_tz.localize(datetime(
        base_date.year,
        base_date.month,
        base_date.day,
        hour,
        minute
    ))

    ist_dt = client_dt.astimezone(ist_tz)

    return client_dt, ist_dt



# from datetime import datetime, timedelta
# import pytz

# WEEKDAYS = {
#     "monday": 0, "tuesday": 1, "wednesday": 2,
#     "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
# }

# def convert_client_time_to_ist(time_str, timezone, date_str=None, weekday=None):
#     client_tz = pytz.timezone(timezone)
#     ist_tz = pytz.timezone("Asia/Kolkata")
#     now_client = datetime.now(client_tz)

#     if date_str:
#         base_date = datetime.fromisoformat(date_str).date()
#     elif weekday:
#         target = WEEKDAYS[weekday.lower()]
#         days_ahead = (target - now_client.weekday()) % 7
#         days_ahead = 7 if days_ahead == 0 else days_ahead
#         base_date = (now_client + timedelta(days=days_ahead)).date()
#     else:
#         raise ValueError("Date or weekday required")

#     hour, minute = map(int, time_str.split(":"))

#     client_dt = client_tz.localize(datetime(
#         base_date.year, base_date.month, base_date.day, hour, minute
#     ))

#     return client_dt, client_dt.astimezone(ist_tz)
