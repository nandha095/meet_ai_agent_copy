import requests
from app.email_provider.base import EmailProvider
from app.services.outlook_reader import fetch_outlook_emails
from app.services.outlook_token_service import get_valid_outlook_access_token


class OutlookProvider(EmailProvider):
    """
    Outlook email provider
    - Reads emails using Microsoft Graph
    - Sends emails using Microsoft Graph
    - Automatically refreshes expired access tokens
    """

    def fetch_recent_emails(self, db, user_id: int):
        """
        Fetch recent emails from Outlook inbox
        """
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
        """
        Send email via Outlook (Microsoft Graph)
        """

        # ✅ ALWAYS get a VALID access token (auto-refresh)
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
                    {
                        "emailAddress": {
                            "address": to_email
                        }
                    }
                ],
            },
            "saveToSentItems": True,
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code not in (200, 202):
            raise Exception(
                f"Outlook sendMail failed: {response.status_code} {response.text}"
            )
