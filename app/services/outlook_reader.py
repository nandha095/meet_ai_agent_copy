import requests
from app.services.outlook_token_service import get_valid_outlook_access_token


def fetch_outlook_emails(db, user_id: int, limit: int = 20):
    """
    Fetch recent emails from Outlook inbox using Microsoft Graph
    """

    access_token = get_valid_outlook_access_token(db, user_id)

    url = (
        "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages"
        "?$top={}&$orderby=receivedDateTime desc"
    ).format(limit)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    messages = response.json().get("value", [])

    emails = []

    for msg in messages:
        emails.append({
            "message_id": msg["id"],
            "from": msg["from"]["emailAddress"]["address"]
            if msg.get("from") else "",
            "subject": msg.get("subject", ""),
            "body": msg.get("body", {}).get("content", ""),
        })

    return emails
