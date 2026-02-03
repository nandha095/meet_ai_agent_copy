from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()  # 👈 THIS IS THE FIX

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

client.messages.create(
    body="SMS test from AI Meeting Scheduler 🚀",
    from_=os.getenv("TWILIO_PHONE_NUMBER"),
    to="+919345649544"  # your verified number
)
