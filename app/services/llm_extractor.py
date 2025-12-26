import json
import os
from typing import Optional

# Example shown with Gemini-style prompt
# You can swap provider later (OpenAI / local LLM)

def llm_extract_intent_and_time(text: str) -> Optional[dict]:
    """
    Returns structured data or None if extraction fails
    """

    prompt = f"""
You are an information extraction engine.

From the email text below, extract:
- intent: one of ["schedule_now", "schedule_later", "no_interest"]
- date: ISO date or null
- time: HH:MM (24h) or null
- timezone: IANA timezone (e.g., America/New_York) or null

Respond ONLY in valid JSON.

Email:
{text}
"""

    try:
        # 🔴 PLACEHOLDER: plug your LLM call here
        # response_text = call_llm(prompt)

        # TEMP example output for testing:
        response_text = """
        {
          "intent": "schedule_later",
          "date": "2025-02-14",
          "time": "21:00",
          "timezone": "America/New_York"
        }
        """

        data = json.loads(response_text)

        # minimal validation
        if "intent" not in data:
            return None

        return data

    except Exception as e:
        print("❌ LLM extraction failed:", e)
        return None


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
#         print("❌ LLM extraction failed:", e)
#         return None
