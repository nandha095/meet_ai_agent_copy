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


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


# -------------------------------------------------
# Proposal email (kept as-is)
# -------------------------------------------------
def send_proposal_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    # Proposal is HTML-only
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD
        )
        server.send_message(msg)


# -------------------------------------------------
# Generic email sender (UPDATED)
# -------------------------------------------------
def send_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: str | None = None
):
    """
    Generic email sender used by all services.
    Supports:
    - Plain text fallback
    - Optional HTML version
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    # Always attach plain-text (fallback)
    msg.attach(MIMEText(body_text, "plain"))

    # Attach HTML if provided
    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD
        )
        server.send_message(msg)
