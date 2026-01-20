import requests
from app.models.outlook_token import OutlookToken
from app.services.outlook_token_service import get_valid_outlook_access_token


GRAPH_MESSAGES_URL = (
    "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages"
)


def fetch_outlook_emails(db, user_id: int, max_results: int = 10):
    """
    Fetch recent Outlook inbox emails
    Returns data in SAME FORMAT as Gmail reader
    """

    access_token = get_valid_outlook_access_token(db, user_id)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    params = {
        "$top": max_results,
        "$orderby": "receivedDateTime desc",
    }

    response = requests.get(
        GRAPH_MESSAGES_URL,
        headers=headers,
        params=params,
    )

    if response.status_code != 200:
        raise Exception(
            f"Outlook inbox fetch failed: {response.text}"
        )

    messages = response.json().get("value", [])

    emails = []

    for msg in messages:
        emails.append({
            "message_id": msg["id"],
            "from": msg.get("from", {})
                .get("emailAddress", {})
                .get("address", ""),
            "subject": msg.get("subject", ""),
            "body": msg.get("body", {}).get("content", ""),
        })

    return emails
