# from datetime import datetime, timedelta
# import pytz
# import re
# from sqlalchemy.exc import IntegrityError

# from app.services.gmail_reader import fetch_recent_emails
# from app.services.ai_intent import detect_meeting_intent
# from app.services.time_extractor import extract_time_and_timezone
# from app.services.meeting_service import create_google_meet
# from app.services.meeting_email_service import (
#     send_meeting_link_email,
#     send_schedule_choice_email
# )
# from app.services.email_cleaner import clean_email_body

# from app.models.reply import Reply
# from app.models.meeting import Meeting

# IST_TZ = pytz.timezone("Asia/Kolkata")


# def extract_email_address(sender: str) -> str:
#     match = re.search(r"<(.+?)>", sender)
#     return match.group(1) if match else sender


# def process_replies(db):
#     emails = fetch_recent_emails()

#     for email in emails:

#         # -------------------------------------------------
#         # 1️⃣ DEDUP BY MESSAGE ID ONLY
#         # -------------------------------------------------
#         if db.query(Reply).filter(
#             Reply.gmail_message_id == email["message_id"]
#         ).first():
#             continue

#         sender_email = extract_email_address(email["from"])
#         clean_body = clean_email_body(email["body"])

#         print("FINAL CLEAN BODY >>>", repr(clean_body))

#         if not clean_body:
#             continue

#         # -------------------------------------------------
#         # 2️⃣ DETECT INTENT
#         # -------------------------------------------------
#         intent = detect_meeting_intent(clean_body)
#         print("INTENT FINAL >>>", intent)

#         # -------------------------------------------------
#         # 3️⃣ SAVE REPLY
#         # -------------------------------------------------
#         reply = Reply(
#             gmail_message_id=email["message_id"],
#             sender=email["from"],
#             subject=email["subject"],
#             body=clean_body,
#             meeting_interest=intent["intent"] != "NO_INTEREST",
#             confidence=intent["confidence"],
#             waiting_for_schedule=False
#         )

#         db.add(reply)
#         db.commit()
#         db.refresh(reply)

#         # -------------------------------------------------
#         # 4️⃣ YES → ASK FOR SCHEDULE
#         # -------------------------------------------------
#         if intent["intent"] == "INTERESTED_NO_TIME":
#             send_schedule_choice_email(sender_email)
#             reply.waiting_for_schedule = True
#             db.commit()
#             continue

#         # -------------------------------------------------
#         # 5️⃣ AUTO-SCHEDULE
#         # -------------------------------------------------
#         if intent["intent"] == "ASKED_TO_SCHEDULE":
#             start_time = datetime.now(IST_TZ) + timedelta(minutes=30)
#             client_time = None
#             client_timezone = None

#         # -------------------------------------------------
#         # 6️⃣ CLIENT PROVIDED TIME
#         # -------------------------------------------------
#         elif intent["intent"] == "CLIENT_PROVIDED_TIME":
#             extracted = extract_time_and_timezone(clean_body)
#             if not extracted:
#                 send_schedule_choice_email(sender_email)
#                 continue

#             start_time = extracted["ist_datetime"]
#             client_time = extracted["client_datetime"]
#             client_timezone = extracted["client_timezone"]

#         else:
#             continue

#         # -------------------------------------------------
#         # 7️⃣ CREATE GOOGLE MEET
#         # -------------------------------------------------
#         meeting_data = create_google_meet(
#             summary="Project Proposal – Discussion",
#             description="Meeting scheduled based on client response",
#             start_time=start_time,
#             duration_minutes=30
#         )

#         meeting = Meeting(
#             reply_id=reply.id,
#             meet_link=meeting_data["meet_link"],
#             start_time=meeting_data["start"],
#             end_time=meeting_data["end"]
#         )

#         db.add(meeting)

#         # -------------------------------------------------
#         # 8️⃣ RESET WAITING STATE
#         # -------------------------------------------------
#         db.query(Reply).filter(
#             Reply.sender == email["from"],
#             Reply.waiting_for_schedule == True
#         ).update({"waiting_for_schedule": False})

#         db.commit()

#         # -------------------------------------------------
#         # 9️⃣ SEND MEETING LINK EMAIL ✅
#         # -------------------------------------------------
#         send_meeting_link_email(
#             to_email=sender_email,
#             meet_link=meeting.meet_link,
#             client_time=client_time,
#             ist_time=start_time,
#             client_timezone=client_timezone
#         )

#         print("✅ Meeting scheduled and email sent to", sender_email)


# from datetime import datetime, timedelta
# import pytz
# import re

# from app.services.gmail_reader import fetch_recent_emails
# from app.services.ai_intent import detect_meeting_intent
# from app.services.time_extractor import extract_time_and_timezone
# from app.services.meeting_service import create_google_meet
# from app.services.meeting_email_service import (
#     send_meeting_link_email,
#     send_schedule_choice_email
# )
# from app.services.email_cleaner import clean_email_body

# from app.models.reply import Reply
# from app.models.meeting import Meeting

# IST_TZ = pytz.timezone("Asia/Kolkata")


# def extract_email_address(sender: str) -> str:
#     match = re.search(r"<(.+?)>", sender)
#     return match.group(1) if match else sender


# def process_replies(db):
#     emails = fetch_recent_emails()

#     for email in emails:

#         # Dedup by message ID only
#         if db.query(Reply).filter(
#             Reply.gmail_message_id == email["message_id"]
#         ).first():
#             continue

#         sender_email = extract_email_address(email["from"])
#         clean_body = clean_email_body(email["body"])

#         print("FINAL CLEAN BODY >>>", repr(clean_body))

#         # 🔥 STEP 3: Ignore junk / non-replies
#         if not clean_body:
#             continue

#         valid_keywords = [
#             "yes", "you can schedule", "schedule",
#             "am", "pm", "ist", "est", "pst", "gmt", "utc"
#         ]

#         if not any(k in clean_body.lower() for k in valid_keywords):
#             continue

#         intent = detect_meeting_intent(clean_body)
#         print("INTENT FINAL >>>", intent)

#         reply = Reply(
#             gmail_message_id=email["message_id"],
#             sender=email["from"],
#             subject=email["subject"],
#             body=clean_body,
#             meeting_interest=intent["intent"] != "NO_INTEREST",
#             confidence=intent["confidence"]
#         )

#         db.add(reply)
#         db.commit()
#         db.refresh(reply)

#         # YES → ask schedule
#         if intent["intent"] == "INTERESTED_NO_TIME":
#             send_schedule_choice_email(sender_email)
#             continue

#         # AUTO-SCHEDULE
#         if intent["intent"] == "ASKED_TO_SCHEDULE":
#             start_time = datetime.now(IST_TZ) + timedelta(minutes=30)
#             client_time = None
#             client_timezone = None

#         # CLIENT PROVIDED TIME
#         elif intent["intent"] == "CLIENT_PROVIDED_TIME":
#             extracted = extract_time_and_timezone(clean_body)
#             if not extracted:
#                 send_schedule_choice_email(sender_email)
#                 continue

#             start_time = extracted["ist_datetime"]
#             client_time = extracted["client_datetime"]
#             client_timezone = extracted["client_timezone"]

#         else:
#             continue

#         meeting_data = create_google_meet(
#             summary="Project Proposal – Discussion",
#             description="Meeting scheduled based on client response",
#             start_time=start_time,
#             duration_minutes=30
#         )

#         meeting = Meeting(
#             reply_id=reply.id,
#             meet_link=meeting_data["meet_link"],
#             start_time=meeting_data["start"],
#             end_time=meeting_data["end"]
#         )

#         db.add(meeting)
#         db.commit()

#         send_meeting_link_email(
#             to_email=sender_email,
#             meet_link=meeting.meet_link,
#             client_time=client_time,
#             ist_time=start_time,
#             client_timezone=client_timezone
#         )

#         print("✅ Meeting scheduled and email sent to", sender_email)


from datetime import datetime, timedelta
import pytz
import re

from app.services.gmail_reader import fetch_recent_emails
from app.services.ai_intent import detect_meeting_intent
from app.services.time_extractor import extract_time_and_timezone
from app.services.meeting_service import create_google_meet
from app.services.meeting_email_service import (
    send_meeting_link_email,
    send_schedule_choice_email
)
from app.services.email_cleaner import clean_email_body

from app.models.reply import Reply
from app.models.meeting import Meeting

IST_TZ = pytz.timezone("Asia/Kolkata")


def extract_email_address(sender: str) -> str:
    match = re.search(r"<(.+?)>", sender)
    return match.group(1) if match else sender


def process_replies(db):
    emails = fetch_recent_emails()

    for email in emails:

        # -------------------------------------------------
        # 1️⃣ DEDUP (message-level)
        # -------------------------------------------------
        if db.query(Reply).filter(
            Reply.gmail_message_id == email["message_id"]
        ).first():
            continue

        sender_email = extract_email_address(email["from"])
        subject = (email.get("subject") or "").lower()

        # -------------------------------------------------
        # 2️⃣ PROCESS ONLY PROPOSAL-RELATED EMAILS
        # -------------------------------------------------
        allowed_subject_keywords = [
            "re: project proposal",
            "re: meeting",
            "meeting sched",
        ]

        if not any(k in subject for k in allowed_subject_keywords):
            continue

        # -------------------------------------------------
        # 3️⃣ BLOCK SYSTEM / MARKETING SENDERS
        # -------------------------------------------------
        blocked_sender_keywords = [
            "linkedin",
            "pinterest",
            "bank",
            "alerts",
            "alert",
            "noreply",
            "no-reply",
            "mailer-daemon",
            "postmaster",
            "newsletter",
        ]

        sender_lower = email["from"].lower()
        if any(bad in sender_lower for bad in blocked_sender_keywords):
            continue

        # -------------------------------------------------
        # 4️⃣ CLEAN EMAIL BODY
        # -------------------------------------------------
        clean_body = clean_email_body(email["body"])
        print("FINAL CLEAN BODY >>>", repr(clean_body))

        if not clean_body:
            continue

        # -------------------------------------------------
        # 5️⃣ IGNORE SYSTEM / BOUNCE CONTENT
        # -------------------------------------------------
        system_indicators = [
            "address not found",
            "mailbox not found",
            "delivery failed",
            "dns error",
            "unable to read queries",
            "this inbox is not monitored",
        ]

        lower_body = clean_body.lower()
        if any(indicator in lower_body for indicator in system_indicators):
            continue

        # -------------------------------------------------
        # 6️⃣ DETECT INTENT
        # -------------------------------------------------
        intent = detect_meeting_intent(clean_body)
        print("INTENT FINAL >>>", intent)

        reply = Reply(
            gmail_message_id=email["message_id"],
            sender=email["from"],
            subject=email["subject"],
            body=clean_body,
            meeting_interest=intent["intent"] != "NO_INTEREST",
            confidence=intent["confidence"]
        )

        db.add(reply)
        db.commit()
        db.refresh(reply)

        # -------------------------------------------------
        # 7️⃣ YES → ASK FOR SCHEDULE
        # -------------------------------------------------
        if intent["intent"] == "INTERESTED_NO_TIME":
            send_schedule_choice_email(sender_email)
            continue

        # -------------------------------------------------
        # 8️⃣ AUTO-SCHEDULE
        # -------------------------------------------------
        if intent["intent"] == "ASKED_TO_SCHEDULE":
            start_time = datetime.now(IST_TZ) + timedelta(minutes=30)
            client_time = None
            client_timezone = None

        # -------------------------------------------------
        # 9️⃣ CLIENT PROVIDED TIME
        # -------------------------------------------------
        elif intent["intent"] == "CLIENT_PROVIDED_TIME":
            extracted = extract_time_and_timezone(clean_body)
            if not extracted:
                send_schedule_choice_email(sender_email)
                continue

            start_time = extracted["ist_datetime"]
            client_time = extracted["client_datetime"]
            client_timezone = extracted["client_timezone"]

        else:
            continue

        # -------------------------------------------------
        # 🔟 CREATE GOOGLE MEET
        # -------------------------------------------------
        meeting_data = create_google_meet(
            summary="Project Proposal – Discussion",
            description="Meeting scheduled based on client response",
            start_time=start_time,
            duration_minutes=30
        )

        meeting = Meeting(
            reply_id=reply.id,
            meet_link=meeting_data["meet_link"],
            start_time=meeting_data["start"],
            end_time=meeting_data["end"]
        )

        db.add(meeting)
        db.commit()

        # -------------------------------------------------
        # 1️⃣1️⃣ SEND MEETING LINK EMAIL
        # -------------------------------------------------
        send_meeting_link_email(
            to_email=sender_email,
            meet_link=meeting.meet_link,
            client_time=client_time,
            ist_time=start_time,
            client_timezone=client_timezone
        )

        print("✅ Meeting scheduled and email sent to", sender_email)
