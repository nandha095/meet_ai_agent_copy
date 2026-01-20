# import json
# import os
# from typing import Optional

# # Example shown with Gemini-style prompt
# # You can swap provider later (OpenAI / local LLM)

# def llm_extract_intent_and_time(text: str) -> Optional[dict]:
#     """
#     Returns structured data or None if extraction fails
#     """

#     prompt = f"""
# You are an information extraction engine.

# From the email text below, extract:
# - intent: one of ["schedule_now", "schedule_later", "no_interest"]
# - date: ISO date or null
# - time: HH:MM (24h) or null
# - timezone: IANA timezone (e.g., America/New_York) or null

# Respond ONLY in valid JSON.

# Email:
# {text}
# """

#     try:
#         #  PLACEHOLDER: plug your LLM call here
#         # response_text = call_llm(prompt)

#         # TEMP example output for testing:
#         response_text = """
#         {
#           "intent": "schedule_later",
#           "date": "2025-02-14",
#           "time": "21:00",
#           "timezone": "America/New_York"
#         }
#         """

#         data = json.loads(response_text)

#         # minimal validation
#         if "intent" not in data:
#             return None

#         return data

#     except Exception as e:
#         print("❌ LLM extraction failed:", e)
#         return None


# import json
# import google.generativeai as genai
# from app.core.config import settings

# genai.configure(api_key=settings.GEMINI_API_KEY)

# MODEL_NAME = "models/gemini-pro"



# SYSTEM_PROMPT = """
# You are an information extraction assistant.
# Extract meeting scheduling details from the text.
# Do NOT guess missing values.
# Return ONLY valid JSON.
# """

# USER_PROMPT_TEMPLATE = """
# Extract meeting scheduling information from the following text.

# Return JSON with these fields ONLY:
# - intent: "schedule" | "interest" | "reject" | "unknown"
# - time: "HH:MM" (24-hour) or null
# - date: "YYYY-MM-DD" or null
# - weekday: monday-sunday or null
# - timezone: IANA timezone like "America/New_York" or null
# - confidence: number between 0 and 1

# Rules:
# - If the text contains rejection, intent = "reject"
# - If time is mentioned without date/weekday, leave date and weekday null
# - Do NOT assume today or tomorrow
# - Do NOT convert timezones
# - If unsure, return null values

# Text:
# <<<EMAIL_TEXT>>>
# """


# def llm_extract_intent_and_time(text: str) -> dict | None:
#     try:
#         model = genai.GenerativeModel(
#             model_name=MODEL_NAME,
#             system_instruction=SYSTEM_PROMPT
#         )

#         prompt = USER_PROMPT_TEMPLATE.replace("<<<EMAIL_TEXT>>>", text)

#         response = model.generate_content(prompt)

#         # Gemini returns text → parse JSON safely
#         extracted = json.loads(response.text)

#         return extracted

#     except Exception as e:
#         print(" LLM extraction failed:", e)
#         return None

import os
import json
from typing import Optional
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set in .env")


def llm_extract_intent_and_time(text: str) -> Optional[dict]:
    print("🤖 OPENAI LLM FUNCTION CALLED")

    today = datetime.utcnow().strftime("%Y-%m-%d")

    prompt = f"""
You are an information extraction engine.

Today's date is: {today}

From the email text below, extract:

- intent: one of ["CLIENT_PROVIDED_TIME", "ASKED_TO_SCHEDULE", "NO_INTEREST", "INTERESTED_NO_TIME"]

- calendar_relative: one of ["today", "tomorrow", "day_after_tomorrow"] or null

- relative_day: one of ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"] or null

- relative_modifier: one of ["this","next"] or null

- time: HH:MM (24h) or null

- timezone: IANA timezone (e.g., Asia/Kolkata, America/New_York) or null

Rules:
- Use calendar_relative ONLY for words like "today", "tomorrow"
- Use relative_day + relative_modifier ONLY for weekday phrases like "next Friday"
- If information is missing, return null
- Return ONLY valid JSON
- No explanations, no markdown

Email:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract structured data from emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        content = response.choices[0].message.content.strip()

        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == -1:
            raise ValueError("No JSON returned by LLM")

        data = json.loads(content[start:end])

        print("🤖 OPENAI PARSED RESULT:", data)
        return data

    except Exception as e:
        print("❌ OpenAI extraction failed:", e)
        return None
