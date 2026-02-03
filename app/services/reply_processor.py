# from datetime import datetime, timedelta
# import pytz
# import re

# from app.services.gmail_reader import fetch_recent_emails
# from app.services.ai_intent import detect_meeting_intent
# from app.services.time_extractor import extract_time_and_timezone
# from app.services.meeting_service import create_google_meet
# from app.services.meeting_email_service import (
#     send_meeting_link_email,
#     send_schedule_choice_email,
#     send_not_interested_email,
# )
# from app.services.email_cleaner import clean_email_body
# from app.services.llm_extractor import llm_extract_intent_and_time

# from app.models.reply import Reply
# from app.models.meeting import Meeting
# from app.models.proposal import Proposal
# from app.models.google_token import GoogleToken

# IST_TZ = pytz.timezone("Asia/Kolkata")


# def extract_email_address(sender: str) -> str:
#     if not sender:
#         return ""
#     match = re.search(r"<(.+?)>", sender)
#     return match.group(1) if match else sender


# def process_replies(db, user_id: int):
#     # 0️⃣ Ensure Google connected
#     token = db.query(GoogleToken).filter(
#         GoogleToken.user_id == user_id
#     ).first()

#     if not token:
#         print(f"⚠️ User {user_id} has no Google token. Skipping.")
#         return

#     emails = fetch_recent_emails(db, user_id)

#     for email in emails:
#         print("\n🔎 Gmail message_id:", email["message_id"])

#         # 1️⃣ Deduplication
#         if db.query(Reply).filter(
#             Reply.gmail_message_id == email["message_id"],
#             Reply.user_id == user_id
#         ).first():
#             print("⏭️ Already processed")
#             continue

#         sender_email = extract_email_address(email.get("from"))

#         # 2️⃣ Block system senders
#         if any(bad in (email.get("from") or "").lower() for bad in [
#             "noreply", "mailer-daemon", "postmaster", "newsletter", "linkedin"
#         ]):
#             continue

#         # 3️⃣ Clean body
#         body = clean_email_body(email.get("body", ""))
#         if not body:
#             continue

#         # 4️⃣ Rule-based intent
#         intent = detect_meeting_intent(body)
#         print("🧠 RULE INTENT:", intent)

#         # 5️⃣ LLM fallback (safe)
#         llm_result = None
#         if intent["confidence"] < 0.75:
#             try:
#                 llm_result = llm_extract_intent_and_time(body)
#             except Exception as e:
#                 print("❌ LLM failed:", e)

#         # 6️⃣ Map LLM → system intents
#         if llm_result:
#             print("🤖 LLM RAW:", llm_result)

#             if llm_result["intent"] == "no_interest":
#                 intent = {"intent": "NO_INTEREST", "confidence": 0.95}

#             elif llm_result["intent"] == "schedule_now":
#                 intent = {"intent": "ASKED_TO_SCHEDULE", "confidence": 0.95}

#             elif llm_result["intent"] == "schedule_later":
#                 intent = {"intent": "INTERESTED_NO_TIME", "confidence": 0.9}

#         print("✅ FINAL INTENT:", intent)

#         # 7️⃣ Find proposal
#         proposal = db.query(Proposal).filter(
#             Proposal.client_email == sender_email,
#             Proposal.user_id == user_id
#         ).order_by(Proposal.created_at.desc()).first()

#         if not proposal:
#             continue

#         # 8️⃣ Save reply
#         reply = Reply(
#             user_id=user_id,
#             proposal_id=proposal.id,
#             gmail_message_id=email["message_id"],
#             sender=email.get("from"),
#             subject=email.get("subject"),
#             body=body,
#             meeting_interest=intent["intent"] != "NO_INTEREST",
#             confidence=intent["confidence"],
#         )

#         db.add(reply)
#         db.commit()
#         db.refresh(reply)

#         # 9️⃣ No interest
#         if intent["intent"] == "NO_INTEREST":
#             proposal.status = "REJECTED"
#             db.commit()
#             send_not_interested_email(db, user_id, sender_email)
#             continue

#         # 🔟 Interested but no time
#         if intent["intent"] == "INTERESTED_NO_TIME":
#             proposal.status = "WAITING_FOR_TIME"
#             db.commit()
#             send_schedule_choice_email(db, user_id, sender_email)
#             continue

#         # 1️⃣1️⃣ Determine meeting time
#         if intent["intent"] == "ASKED_TO_SCHEDULE":
#             start_time = datetime.now(IST_TZ) + timedelta(minutes=30)
#             client_time = None
#             client_timezone = None

#         else:
#             extracted = extract_time_and_timezone(body)
#             if not extracted:
#                 send_schedule_choice_email(db, user_id, sender_email)
#                 continue

#             start_time = extracted["ist_datetime"]
#             client_time = extracted["client_datetime"]
#             client_timezone = extracted["client_timezone"]

#         # 1️⃣2️⃣ Prevent duplicate meetings
#         if db.query(Meeting).filter(
#             Meeting.reply_id == reply.id,
#             Meeting.user_id == user_id
#         ).first():
#             continue

#         # 1️⃣3️⃣ Create Google Meet
#         meeting_data = create_google_meet(
#             db=db,
#             user_id=user_id,
#             summary="Project Proposal – Discussion",
#             description="Meeting scheduled based on client response",
#             start_time=start_time,
#             duration_minutes=30,
#         )

#         meeting = Meeting(
#             user_id=user_id,
#             proposal_id=proposal.id,
#             reply_id=reply.id,
#             meet_link=meeting_data["meet_link"],
#             start_time=meeting_data["start_time"],
#             end_time=meeting_data["end_time"],
#         )

#         db.add(meeting)
#         proposal.status = "MEETING_SCHEDULED"
#         db.commit()

#         # 1️⃣4️⃣ Send meeting email
#         send_meeting_link_email(
#             db=db,
#             user_id=user_id,
#             to_email=sender_email,
#             meet_link=meeting.meet_link,
#             client_time=client_time,
#             ist_time=start_time,
#             client_timezone=client_timezone,
#         )

#         print("✅ Meeting scheduled & email sent")

# reply_processor.py

from datetime import datetime, timedelta
import pytz
import re

from app.services.ai_intent import detect_meeting_intent
from app.services.time_extractor import extract_time_and_timezone
from app.services.llm_extractor import llm_extract_intent_and_time
from app.services.meeting_service import create_google_meet
from app.services.email_cleaner import clean_email_body
from app.services.timezone_utils import (
    convert_calendar_relative_to_ist,
)
from app.services.meeting_email_service import (
    send_schedule_choice_email,
    send_meeting_link_email,
    send_not_interested_email,
    send_reschedule_options_email,
)
from app.services.availability_service import find_alternative_slots
from app.services.phone_utils import extract_phone, normalize_phone
from app.services.sms_service import send_meeting_sms
from app.services.google_availability_service import is_google_calendar_free

from app.models.reply import Reply
from app.models.meeting import Meeting
from app.models.proposal import Proposal
from app.models.user import User
from app.email_provider.factory import get_email_provider


IST_TZ = pytz.timezone("Asia/Kolkata")

SYSTEM_SENDERS = ("no-reply@", "noreply@", "mailer-daemon@")
AMBIGUOUS_PHRASES = (
    "sometime",
    "anytime",
    "whenever",
    "flexible",
    "your convenience",
    "evening works",
    "morning works",
)

TIME_KEYWORDS = ("am", "pm", "ist", "est", "pst", "gmt")


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def normalize_ordinal_dates(text: str) -> str:
    return re.sub(r"(\d+)(st|nd|rd|th)", r"\1", text, flags=re.IGNORECASE)


def remove_phone_from_text(text: str) -> str:
    return re.sub(r"\+?\d[\d\s\-]{8,}", "", text)


def extract_time_text_only(body: str) -> str:
    for line in body.splitlines():
        if any(k in line.lower() for k in TIME_KEYWORDS):
            return line.strip()
    return body


def is_ambiguous_time(text: str) -> bool:
    return any(p in text.lower() for p in AMBIGUOUS_PHRASES)


def extract_email(sender: str) -> str:
    if not sender:
        return ""
    match = re.search(r"<(.+?)>", sender)
    return (match.group(1) if match else sender).strip().lower()


# -------------------------------------------------
# MAIN PROCESSOR
# -------------------------------------------------
def process_replies(db, user_id: int):
    print("🔥 process_replies CALLED for user_id:", user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    proposals = (
        db.query(Proposal)
        .filter(
            Proposal.user_id == user_id,
            Proposal.status.in_(
                ["SENT", "WAITING_FOR_TIME", "WAITING_FOR_RESCHEDULE"]
            ),
        )
        .all()
    )

    if not proposals:
        return

    provider_map = {}
    for p in proposals:
        provider_map.setdefault(p.provider or "google", []).append(p)

    for provider_name in provider_map:
        provider = get_email_provider(provider_name)

        try:
            emails = provider.fetch_recent_emails(db, user_id)
        except Exception as e:
            print(f"⚠️ Skipping {provider_name}: {e}")
            continue

        print(f"📤 Reading inbox via {provider_name.upper()}")

        for email in emails:
            try:
                raw_id = email.get("message_id")
                sender_email = extract_email(email.get("from"))

                if not raw_id or not sender_email:
                    continue
                if sender_email.startswith(SYSTEM_SENDERS):
                    continue
                if sender_email == user.email.lower():
                    continue

                msg_id = f"{provider_name}:{raw_id}"
                if db.query(Reply).filter_by(gmail_message_id=msg_id).first():
                    continue

                body = clean_email_body(email.get("body", ""))
                body = normalize_ordinal_dates(body)

                body_no_phone = remove_phone_from_text(body)
                time_text = extract_time_text_only(body_no_phone)

                proposal = (
                    db.query(Proposal)
                    .filter(
                        Proposal.user_id == user_id,
                        Proposal.provider == provider_name,
                        Proposal.client_email.ilike(f"%{sender_email}%"),
                    )
                    .order_by(Proposal.created_at.desc())
                    .first()
                )
                if not proposal:
                    continue

                rule_intent = detect_meeting_intent(body)

                reply = Reply(
                    user_id=user_id,
                    proposal_id=proposal.id,
                    gmail_message_id=msg_id,
                    sender=email.get("from"),
                    subject=email.get("subject"),
                    body=body,
                    meeting_interest=rule_intent["intent"] != "NO_INTEREST",
                    confidence=rule_intent.get("confidence", 0.8),
                )
                db.add(reply)
                db.commit()

                # 📞 Phone
                phone = extract_phone(body)
                if phone and not proposal.client_phone:
                    proposal.client_phone = normalize_phone(phone)
                    db.commit()

                # ❌ Not interested
                if rule_intent["intent"] == "NO_INTEREST":
                    proposal.status = "REJECTED"
                    db.commit()
                    send_not_interested_email(
                        db, user_id, sender_email, provider_name
                    )
                    continue

                # First accept → ask time
                if proposal.status == "SENT":
                    proposal.status = "WAITING_FOR_TIME"
                    db.commit()
                    send_schedule_choice_email(
                        db, user_id, sender_email, provider_name
                    )
                    continue

                client_dt = ist_dt = client_tz = None

                # Auto schedule
                if "you can schedule" in body.lower():
                    ist_dt = datetime.now(IST_TZ) + timedelta(minutes=30)
                    client_dt = ist_dt
                    client_tz = "Asia/Kolkata"

                # Explicit time
                if not ist_dt:
                    extracted = extract_time_and_timezone(time_text)
                    if extracted:
                        client_dt = extracted["client_datetime"]
                        ist_dt = extracted["ist_datetime"]
                        client_tz = extracted["client_timezone"]

                # Ambiguous → LLM
                if not ist_dt and is_ambiguous_time(body):
                    llm = llm_extract_intent_and_time(body)
                    if llm and llm.get("time"):
                        client_dt, ist_dt = convert_calendar_relative_to_ist(
                            llm["time"],
                            llm["timezone"],
                            llm.get("calendar_relative"),
                        )
                        client_tz = llm["timezone"]

                if not ist_dt:
                    print("⚠️ Time parsing failed for:", time_text)
                    continue

                start = ist_dt
                end = ist_dt + timedelta(minutes=30)

                # 🔥 GOOGLE CALENDAR CONFLICT CHECK (PRIMARY)
                google_free = is_google_calendar_free(
                    db, user_id, start, end
                )

                if not google_free:
                    alternatives = find_alternative_slots(db, user_id, start)
                    proposal.status = "WAITING_FOR_RESCHEDULE"
                    db.commit()

                    send_reschedule_options_email(
                        db,
                        user_id,
                        sender_email,
                        provider_name,
                        start,
                        alternatives,
                    )
                    print("📧 Google Calendar conflict → reschedule sent")
                    continue

                # ✅ Create meeting
                meeting_data = create_google_meet(
                    db=db,
                    user_id=user_id,
                    summary="Project Proposal – Discussion",
                    description="Meeting scheduled after client confirmation",
                    start_time=start,
                    duration_minutes=30,
                )

                meeting = Meeting(
                    user_id=user_id,
                    proposal_id=proposal.id,
                    reply_id=reply.id,
                    meet_link=meeting_data["meet_link"],
                    start_time=meeting_data["start_time"],
                    end_time=meeting_data["end_time"],
                )

                db.add(meeting)
                proposal.status = "MEETING_SCHEDULED"
                db.commit()

                # Emails
                send_meeting_link_email(
                    db,
                    user_id,
                    sender_email,
                    meeting.meet_link,
                    client_dt,
                    ist_dt,
                    client_tz,
                    provider_name,
                )

                notify_email = (
                    user.outlook_email
                    if proposal.provider == "outlook"
                    else user.email
                )

                send_meeting_link_email(
                    db,
                    user_id,
                    notify_email,
                    meeting.meet_link,
                    client_dt,
                    ist_dt,
                    client_tz,
                    provider_name,
                )

                # SMS (best effort)
                if proposal.client_phone:
                    try:
                        send_meeting_sms(
                            proposal.client_phone,
                            meeting.meet_link,
                            meeting.start_time,
                        )
                        print("📩 SMS sent")
                    except Exception as e:
                        print("⚠️ SMS failed:", e)

                print("✅ Meeting scheduled")

            except Exception as e:
                db.rollback()
                print("❌ Reply processing error:", e)
