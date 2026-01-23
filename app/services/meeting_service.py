from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from googleapiclient.discovery import build

from app.services.google_credentials import get_google_credentials


def get_calendar_service(db: Session, user_id: int):
    """
    Returns Google Calendar service for a specific user
    """
    creds = get_google_credentials(db, user_id)
    return build("calendar", "v3", credentials=creds)


def create_google_meet(
    db: Session,
    user_id: int,
    summary: str,
    description: str,
    start_time: datetime,
    duration_minutes: int = 60,
    timezone: str = "Asia/Kolkata",
):
    """
    Creates a Google Meet event for a specific user
    """
    service = get_calendar_service(db, user_id)
    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": timezone,
        },
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{int(datetime.utcnow().timestamp())}"
            }
        }
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1
    ).execute()

    conference = created_event.get("conferenceData", {})
    entry_points = conference.get("entryPoints", [])

    if not entry_points:
        raise Exception("Google Meet link was not created")

    return {
        "meet_link": entry_points[0]["uri"],
        "start_time": start_time,
        "end_time": end_time,
    }
