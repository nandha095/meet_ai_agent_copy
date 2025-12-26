import base64
import email
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    creds = Credentials.from_authorized_user_file(
        "gmail_token.json", SCOPES
    )
    return build("gmail", "v1", credentials=creds)


def fetch_recent_emails():
    service = get_gmail_service()

    # 🔥 only inbox, not sent by you, not mailer-daemon
    results = service.users().messages().list(
        userId="me",
        q="is:inbox -from:me -from:mailer-daemon -from:postmaster"
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="raw"
        ).execute()

        raw = base64.urlsafe_b64decode(msg_data["raw"])
        email_msg = email.message_from_bytes(raw)

        body = ""
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() in ["text/plain", "text/html"]:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = email_msg.get_payload(decode=True).decode(errors="ignore")

        emails.append({
            "message_id": msg["id"],
            "from": email_msg.get("From"),
            "subject": email_msg.get("Subject"),
            "body": body
        })

    return emails
