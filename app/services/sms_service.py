from twilio.rest import Client
import os

def send_meeting_sms(phone: str, meet_link: str, start_time):
    print(Client)

    """
    Sends SMS with meeting link using Twilio.
    Called ONLY if phone number exists.
    """
    client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )

    body = (
        "📅 Meeting Scheduled\n\n"
        f"🕒 {start_time}\n"
        f"🔗 Join: {meet_link}\n\n"
        "Looking forward to connecting!"
    )

    client.messages.create(
        body=body,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=phone
    )
