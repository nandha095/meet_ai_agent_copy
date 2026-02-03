from datetime import datetime
import pytz
from googleapiclient.discovery import build

from app.services.gmail_auth import get_google_credentials



def is_google_calendar_free(
    db,
    user_id: int,
    start_time: datetime,
    end_time: datetime,
) -> bool:
    """
    Returns True if user is FREE in Google Calendar
    Returns False if BUSY
    """

    creds = get_google_credentials(db, user_id)
    if not creds:
        # If Google not connected, assume free
        return True

    service = build("calendar", "v3", credentials=creds)

    body = {
        "timeMin": start_time.astimezone(pytz.UTC).isoformat(),
        "timeMax": end_time.astimezone(pytz.UTC).isoformat(),
        "items": [{"id": "primary"}],
    }

    result = service.freebusy().query(body=body).execute()

    busy_times = result["calendars"]["primary"]["busy"]

    # If busy list is empty → FREE
    return len(busy_times) == 0
