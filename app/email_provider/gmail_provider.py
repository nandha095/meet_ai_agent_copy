from app.email_provider.base import EmailProvider
from app.services.gmail_reader import fetch_recent_emails
from app.services.email_service import send_proposal_email


class GmailProvider(EmailProvider):

    def fetch_recent_emails(self, db, user_id: int):
        return fetch_recent_emails(db, user_id)

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
        Uses existing Gmail proposal email logic
        """

        send_proposal_email(
            db=db,
            user_id=user_id,
            to_email=to_email,
            subject=subject,
            body=body_html,
        )
