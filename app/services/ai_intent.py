# interest_phrases = [
#     # Simple yes
#     "yes",
#     "yep",
#     "yeah",
#     "yup",

#     # Acknowledgements
#     "ok",
#     "okay",
#     "alright",
#     "sure",
#     "fine",
#     "cool",

#     # Polite / business
#     "interested",
#     "sounds good",
#     "that works",
#     "works for me",
#     "fine with me",
#     "happy to proceed",
#     "looking forward",
#     "approved",
#     "confirmed",

#     # Short email replies
#     "yes please",
#     "okay thanks",
#     "sure thanks",
#     "thanks, yes",
# ]

# def detect_meeting_intent(text: str):
#     if not text:
#         return {"intent": "NO_INTEREST", "confidence": 0.5}

#     t = text.lower().strip()

#     # Highest priority
#     if "you can schedule" in t:
#         return {"intent": "ASKED_TO_SCHEDULE", "confidence": 0.95}

#     # Time provided
#     if any(x in t for x in ["am", "pm"]) and any(z in t for z in ["ist", "est", "pst", "gmt", "utc"]):
#         return {"intent": "CLIENT_PROVIDED_TIME", "confidence": 0.9}

#     # Interest
#     # if any(w in t for w in ["yes", "ok", "okay", "sure", "interested", "sounds good"]):
#     #     return {"intent": "INTERESTED_NO_TIME", "confidence": 0.7}
#     if any(p in t for p in interest_phrases):
#         return {"intent": "INTERESTED_NO_TIME", "confidence": 0.7}

#     return {"intent": "NO_INTEREST", "confidence": 0.5}


import re

interest_phrases = [
    "yes", "yep", "yeah", "yup",
    "ok", "okay", "alright", "sure", "fine", "cool",
    "interested", "sounds good", "that works", "works for me",
    "fine with me", "happy to proceed", "looking forward",
    "approved", "confirmed",
    "yes please", "okay thanks", "sure thanks", "thanks, yes", "happy to move forward", 
    "glad to proceed", "let's do it", "let us proceed", "excited to start",
    "we agree", "we are on board", "proceed as discussed","looking forward to working together",
    "great, let's proceed", "let's get started","im interested","interested in moving forward",
]

NO_INTEREST_PATTERNS = [
    r"\bno\b",
    r"\bno thanks\b",
    r"\bnot interested\b",
    r"\bnot interested now\b",
    r"\bnot required\b",
    r"\bno need\b",
    r"\bdo not want\b",
    r"\bwon't work\b",
    r"\bnot looking\b",
    r"\bmaybe later\b",
    r"\bsorry not interested\b",
    r"\bnot to proceed\b",
    r"\bwe are not interested\b",
    r"\bdecline\b",
    r"\bdeclined\b",
    r"\breject\b",
    r"\brejected\b",
]

def detect_meeting_intent(text: str):
    if not text or not text.strip():
        return {"intent": "UNKNOWN", "confidence": 0.3}

    t = text.lower().strip()

    # 0️ No interest
    for pattern in NO_INTEREST_PATTERNS:
        if re.search(pattern, t):
            return {"intent": "NO_INTEREST", "confidence": 0.95}

    # 1️ Asked to schedule
    if re.search(r"\b(you can schedule|please schedule|go ahead and schedule)\b", t):
        return {"intent": "ASKED_TO_SCHEDULE", "confidence": 0.95}

    # 2️ Time provided (AM/PM or HH:MM with optional timezone)
    if re.search(r"\b(\d{1,2}(:\d{2})?\s?(am|pm))\b", t) or \
       re.search(r"\b\d{1,2}:\d{2}\b", t):
        if re.search(r"\b(ist|est|pst|gmt|utc|edt|pdt|mdt|mst|cdt|cst|)\b", t):
            return {"intent": "CLIENT_PROVIDED_TIME", "confidence": 0.9}

    # 3️ Interest without time
    for phrase in interest_phrases:
        if re.search(rf"\b{re.escape(phrase)}\b", t):
            confidence = 0.8 if len(phrase.split()) > 1 else 0.7
            return {"intent": "INTERESTED_NO_TIME", "confidence": confidence}

    return {"intent": "NO_INTEREST", "confidence": 0.5}

