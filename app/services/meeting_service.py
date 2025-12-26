from datetime import datetime, timedelta
from app.services.google_calendar import get_calendar_service


def create_google_meet(summary, description, start_time, duration_minutes=30):
    service = get_calendar_service()
    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata",
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
        raise Exception("Google Meet link not created")

    return {
        "meet_link": entry_points[0]["uri"],
        "start": start_time,
        "end": end_time
    }
