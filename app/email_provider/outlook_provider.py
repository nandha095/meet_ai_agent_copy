import requests
from app.email_provider.base import EmailProvider
from app.services.outlook_reader import fetch_outlook_emails
from app.services.outlook_token_service import get_valid_outlook_access_token


class OutlookProvider(EmailProvider):

    def fetch_recent_emails(self, db, user_id: int):
        return fetch_outlook_emails(db, user_id)

    def send_email(
        self,
        db,
        user_id: int,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str = None,
    ):
        access_token = get_valid_outlook_access_token(db, user_id)

        url = "https://graph.microsoft.com/v1.0/me/sendMail"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body_html,
                },
                "toRecipients": [
                    {"emailAddress": {"address": to_email}}
                ],
            },
            "saveToSentItems": True,
        }

        res = requests.post(url, headers=headers, json=payload)

        if res.status_code not in (200, 202):
            raise Exception(res.text)
