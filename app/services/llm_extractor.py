
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
