# from app.services.email_service import send_email
# from datetime import datetime


# def send_meeting_link_email(
#     to_email,
#     meet_link,
#     client_time,
#     ist_time,
#     client_timezone
# ):
#     subject = "Meeting Scheduled – Google Meet Link"

#     # -------------------------------------------------
#     # Time section (client time + IST if available)
#     # -------------------------------------------------
#     if client_time and client_timezone:
#         time_section = f"""
# 📅 Meeting Time ({client_timezone}):
# {client_time.strftime('%d %b %Y, %I:%M %p')} {client_timezone}

# 📍 Meeting Time (IST):
# {ist_time.strftime('%d %b %Y, %I:%M %p')} IST
# """
#     else:
#         time_section = f"""
# 📍 Meeting Time (IST):
# {ist_time.strftime('%d %b %Y, %I:%M %p')} IST
# """

#     # -------------------------------------------------
#     # Email body
#     # -------------------------------------------------
#     body = f"""
# Hi,

# ✅ Your meeting has been scheduled successfully.

# 🔗 Google Meet Link:
# {meet_link}

# {time_section}

# If this time doesn’t work for you, please reply to this email and we can reschedule.

# Best regards,  
# Nandhakumar
# """

#     send_email(to_email, subject, body)


# def send_schedule_choice_email(to_email):
#     """
#     Sent when client is interested but did not provide time.
#     """
#     subject = "Meeting Scheduling – Next Steps"

#     body = """
# Hi,

# Thank you for your interest in our proposal.

# To schedule our meeting, please choose one of the following options:

# 1️⃣ Reply with your preferred date, time, and timezone  
#    Example: "Friday, December 27th at 9:00 PM EST"

# 2️⃣ Or simply reply with:
#    "You can schedule"

# I’ll take care of the rest.

# Looking forward to connecting with you.

# Best regards,  
# Nandhakumar
# """

#     send_email(to_email, subject, body)
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session

from app.services.gmail_reader import get_gmail_service


# -------------------------------------------------
# SEND MEETING LINK EMAIL (GMAIL API – MULTI USER)
# -------------------------------------------------
def send_meeting_link_email(
    db: Session,
    user_id: int,
    to_email: str,
    meet_link: str,
    client_time,
    ist_time,
    client_timezone
):
    service = get_gmail_service(db, user_id)

    subject = "Meeting Scheduled – Google Meet Link"

    # -------- TEXT VERSION (fallback) --------
    if client_time and client_timezone:
        text_time = (
            f"Meeting Time ({client_timezone}):\n"
            f"{client_time.strftime('%d %b %Y, %I:%M %p')} {client_timezone}\n\n"
            f"Meeting Time (IST):\n"
            f"{ist_time.strftime('%d %b %Y, %I:%M %p')} IST\n"
        )
    else:
        text_time = (
            f"Meeting Time (IST):\n"
            f"{ist_time.strftime('%d %b %Y, %I:%M %p')} IST\n"
        )

    body_text = (
        "Hi,\n\n"
        "Your meeting has been scheduled successfully.\n\n"
        "Google Meet Link:\n"
        f"{meet_link}\n\n"
        f"{text_time}\n"
        "If this time doesn’t work for you, please reply to this email and we can reschedule.\n\n"
        "Best regards,\n"
        "Nandhakumar P"
    )

    # -------- HTML VERSION --------
    if client_time and client_timezone:
        html_time = f"""
        <p><strong>Meeting Time ({client_timezone}):</strong><br>
        {client_time.strftime('%d %b %Y, %I:%M %p')} {client_timezone}</p>

        <p><strong>Meeting Time (IST):</strong><br>
        {ist_time.strftime('%d %b %Y, %I:%M %p')} IST</p>
        """
    else:
        html_time = f"""
        <p><strong>Meeting Time (IST):</strong><br>
        {ist_time.strftime('%d %b %Y, %I:%M %p')} IST</p>
        """

    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Hi,</p>

        <p><strong>Your meeting has been scheduled successfully.</strong></p>

        <p>
          <strong>Google Meet Link:</strong><br><br>
          <a href="{meet_link}"
             style="
               display:inline-block;
               padding:12px 20px;
               background-color:#1a73e8;
               color:#ffffff;
               text-decoration:none;
               border-radius:4px;
               font-weight:bold;
             ">
            Join Google Meet
          </a>
        </p>

        {html_time}

        <p>
          If this time doesn’t work for you, simply reply to this email and we can reschedule.
        </p>

        <p>
          Best regards,<br>
          <strong>Nandhakumar P</strong>
        </p>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    raw = base64.urlsafe_b64encode(
        msg.as_bytes()
    ).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()


# -------------------------------------------------
# ASK CLIENT TO SHARE TIME (GMAIL API)
# -------------------------------------------------
def send_schedule_choice_email(db: Session, user_id: int, to_email: str):
    service = get_gmail_service(db, user_id)

    subject = "Meeting Scheduling – Next Steps"

    # body_text = (
    #     "Hi,\n\n"
    #     "Thank you for your interest in our proposal.\n\n"
    #     "To schedule our meeting, please choose one of the following:\n\n"
    #     "1. Reply with your preferred date, time, and timezone\n"
    #     "   Example: Friday, December 27th at 9:00 PM EST\n\n"
    #     "2. Or simply reply with:\n"
    #     "   You can schedule\n\n"
    #     "Looking forward to connecting with you.\n\n"
    #     "Best regards,\n"
    #     "Nandhakumar P"
    # )

    body_html = """
    <html>
      <body style="font-family: Arial, sans-serif;">
        <p>Hi,</p>
        <p>Thank you for your interest in our proposal.</p>
        <p>To schedule our meeting, please choose one of the following:</p>
        <ul>
          <li>Reply with your preferred <strong>date, time, and timezone</strong></li>
          <li>Example: <em>Friday, December 27th at 9:00 PM EST</em></li>
          <li>Or reply with <strong>You can schedule</strong></li>
        </ul>
        <p>Looking forward to connecting.</p>
        <p><strong>Nandhakumar P</strong></p>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["To"] = to_email
    msg["Subject"] = subject
    # msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()


# -------------------------------------------------
# NOT INTERESTED EMAIL (GMAIL API)
# -------------------------------------------------
def send_not_interested_email(db: Session, user_id: int, to_email: str):
    service = get_gmail_service(db, user_id)

    subject = "Thank you for your response"
    body = (
        "Hi,\n\n"
        "Thank you for letting us know.\n\n"
        "No problem at all — if you’d like to connect in the future, "
        "feel free to reach out anytime.\n\n"
        "Best regards,\n"
        "Nandhakumar"
    )
    
    msg = MIMEText(body, "plain")
    msg["To"] = to_email
    msg["Subject"] = subject

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()
