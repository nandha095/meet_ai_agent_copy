import json
import os
import re
from datetime import datetime
from typing import Optional

import pytz
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

ALLOWED_INTENTS = {
    "CLIENT_PROVIDED_TIME",
    "ASKED_TO_SCHEDULE",
    "NO_INTEREST",
    "INTERESTED_NO_TIME",
}
ALLOWED_CALENDAR_RELATIVE = {"today", "tomorrow", "day_after_tomorrow", None}
ALLOWED_RELATIVE_MODIFIER = {"this", "next", None}
ALLOWED_RELATIVE_DAY = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    None,
}


def _normalize_time(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    v = value.strip().lower()

    # Already HH:MM
    if re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", v):
        return v

    # 12-hour format (e.g. 6:30 pm, 6 pm)
    m = re.fullmatch(r"(\d{1,2})(?::([0-5]\d))?\s*(am|pm)", v)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2) or "00")
        ap = m.group(3)

        if hour < 1 or hour > 12:
            return None

        if ap == "pm" and hour != 12:
            hour += 12
        if ap == "am" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute:02d}"

    return None


def _valid_iana_timezone(tz: Optional[str]) -> Optional[str]:
    if not tz:
        return None
    try:
        pytz.timezone(tz)
        return tz
    except Exception:
        return None


def llm_extract_intent_and_time(text: str) -> Optional[dict]:
    print("ollama LLM FUNCTION CALLED")

    today = datetime.utcnow().strftime("%Y-%m-%d")

    prompt = f"""
You are an information extraction engine.

Today's date is: {today}

Extract ONLY this JSON object with these keys:
- intent: one of ["CLIENT_PROVIDED_TIME", "ASKED_TO_SCHEDULE", "NO_INTEREST", "INTERESTED_NO_TIME"]
- calendar_relative: one of ["today", "tomorrow", "day_after_tomorrow"] or null
- relative_day: one of ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"] or null
- relative_modifier: one of ["this","next"] or null
- time: HH:MM in 24h format or null
- timezone: IANA timezone (e.g., Asia/Kolkata, America/New_York) or null

Strict rules:
- IST must map to Asia/Kolkata.
- If explicit time is provided, prefer intent = CLIENT_PROVIDED_TIME.
- If info is missing, return null for that field.
- Return JSON only. No prose, no markdown, no extra keys.

Email text:
{text}
"""

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You extract structured scheduling data from emails.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
            },
            timeout=120,
        )
        resp.raise_for_status()
        raw = resp.json()

        content = (raw.get("message", {}) or {}).get("content", "")
        if not content:
            return None

        data = json.loads(content)

        # Keep only expected keys
        result = {
            "intent": data.get("intent"),
            "calendar_relative": data.get("calendar_relative"),
            "relative_day": data.get("relative_day"),
            "relative_modifier": data.get("relative_modifier"),
            "time": data.get("time"),
            "timezone": data.get("timezone"),
        }

        # Validate enums
        if result["intent"] not in ALLOWED_INTENTS:
            return None

        if result["calendar_relative"] not in ALLOWED_CALENDAR_RELATIVE:
            result["calendar_relative"] = None

        if result["relative_modifier"] not in ALLOWED_RELATIVE_MODIFIER:
            result["relative_modifier"] = None

        day = result["relative_day"]
        if isinstance(day, str):
            day = day.lower().strip()
        if day not in ALLOWED_RELATIVE_DAY:
            day = None
        result["relative_day"] = day

        # Normalize "next week" wording from raw text
        lower_text = text.lower()
        if "next week" in lower_text:
            result["relative_modifier"] = "next"

        if result["relative_day"] is None:
            result["relative_modifier"] = None


        result["time"] = _normalize_time(result["time"])
        if result["time"] is None and result["intent"] == "ASKED_TO_SCHEDULE":
            result["intent"] = "INTERESTED_NO_TIME"


        # Timezone correction for IST mentions
        if re.search(r"\bist\b", text, flags=re.IGNORECASE):
            result["timezone"] = "Asia/Kolkata"
        else:
            result["timezone"] = _valid_iana_timezone(result["timezone"])

        return result

    except Exception as e:
        print("Ollama extraction failed:", e)
        return None
