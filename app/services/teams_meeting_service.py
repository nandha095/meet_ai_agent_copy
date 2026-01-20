import requests
from datetime import datetime, timedelta
from app.services.outlook_token_service import get_valid_outlook_access_token

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


def create_teams_meeting(
    db,
    user_id: int,
    subject: str,
    start_time: datetime,
    duration_minutes: int = 30,
    timezone: str = "Asia/Kolkata",
):
    """
    Create a Microsoft Teams meeting using Microsoft Graph.
    
    IMPORTANT:
    - start_time MUST match the timezone
    - timezone MUST be the client's real timezone (e.g. America/New_York)
    """

    # 🔐 Always fetch a valid (auto-refreshed) token
    access_token = get_valid_outlook_access_token(db, user_id)

    if not access_token:
        raise Exception("Outlook access token missing")

    if not start_time or not timezone:
        raise Exception("start_time or timezone missing for Teams meeting")

    end_time = start_time + timedelta(minutes=duration_minutes)

    url = f"{GRAPH_BASE_URL}/me/events"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "subject": subject,
        "start": {
        "dateTime": start_time.isoformat(),
        "timeZone": timezone,
        },
        "end": {
        "dateTime": end_time.isoformat(),
        "timeZone": timezone,
        },
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code not in (200, 201):
        raise Exception(
            f"Teams meeting failed: {response.status_code} {response.text}"
        )

    data = response.json()
    
    print("🔍 DEBUG - API Response:", data)  # ← ADD THIS LINE

    # 🛡️ Safety check
    if "onlineMeeting" not in data or not data.get("onlineMeeting") or "joinUrl" not in data["onlineMeeting"]:
        raise Exception("Teams meeting created but joinUrl missing")

    return {
        "meeting_link": data["onlineMeeting"]["joinUrl"],
        "start_time": start_time,
        "end_time": end_time,
        "timezone": timezone,
    }