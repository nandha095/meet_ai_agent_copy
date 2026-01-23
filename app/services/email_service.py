# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from app.core.config import settings


# def send_proposal_email(to_email: str, subject: str, body: str):
#     msg = MIMEMultipart()
#     msg["From"] = settings.EMAIL_HOST_USER
#     msg["To"] = to_email
#     msg["Subject"] = subject

#     msg.attach(MIMEText(body, "html"))

#     server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
#     server.starttls()
#     server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#     server.send_message(msg)
#     server.quit()

# def send_email(to_email: str, subject: str, body: str):
#     """
#     Generic email sender used by all services
#     """
#     from email.mime.text import MIMEText
#     import smtplib
#     from app.core.config import settings

#     msg = MIMEText(body, "html")
#     msg["Subject"] = subject
#     msg["From"] = settings.EMAIL_HOST_USER
#     msg["To"] = to_email

#     with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
#         server.starttls()
#         server.login(
#             settings.EMAIL_HOST_USER,
#             settings.EMAIL_HOST_PASSWORD
#         )
#         server.send_message(msg)

import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from sqlalchemy.orm import Session

from app.services.gmail_reader import get_gmail_service
from app.core.config import settings


# =================================================
# USER EMAIL (GMAIL API – MULTI USER, WITH ATTACHMENTS)
# =================================================
def send_proposal_email(
    db: Session,
    user_id: int,
    to_email: str,
    subject: str,
    body: str,
    attachments=None
):
    """
    Sends proposal email using the logged-in user's Gmail account
    (Gmail API, per-user Google OAuth)
    Supports file attachments
    """

    service = get_gmail_service(db, user_id)

    # Create email container
    msg = MIMEMultipart()
    msg["To"] = to_email
    msg["Subject"] = subject

    # Email body (HTML)
    msg.attach(MIMEText(body, "html"))

    # Attach files (if any)
    if attachments:
        for file in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{file.filename}"'
            )
            msg.attach(part)

    # Encode message for Gmail API
    raw_message = base64.urlsafe_b64encode(
        msg.as_bytes()
    ).decode("utf-8")

    # Send via Gmail API
    service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()


# =================================================
# SYSTEM EMAIL (SMTP – APP OWN EMAIL)  NO CHANGE
# =================================================
def send_system_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: str | None = None
):
    """
    Used ONLY for system emails:
    - Forgot password
    - Reset password
    - Admin alerts
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body_text, "plain"))

    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD
        )
        server.send_message(msg)
