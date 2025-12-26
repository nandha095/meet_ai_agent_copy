def detect_meeting_intent(text: str):
    if not text:
        return {"intent": "NO_INTEREST", "confidence": 0.5}

    t = text.lower().strip()

    # Highest priority
    if "you can schedule" in t:
        return {"intent": "ASKED_TO_SCHEDULE", "confidence": 0.95}

    # Time provided
    if any(x in t for x in ["am", "pm"]) and any(z in t for z in ["ist", "est", "pst", "gmt", "utc"]):
        return {"intent": "CLIENT_PROVIDED_TIME", "confidence": 0.9}

    # Interest
    if any(w in t for w in ["yes", "ok", "okay", "sure", "interested", "sounds good"]):
        return {"intent": "INTERESTED_NO_TIME", "confidence": 0.7}

    return {"intent": "NO_INTEREST", "confidence": 0.5}
