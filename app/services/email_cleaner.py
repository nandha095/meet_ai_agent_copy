import re
from html import unescape


def clean_email_body(text: str) -> str:
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove quoted replies
    patterns = [
        r"\bon .* wrote\b.*",
        r"\bfrom:.*",
        r"\bsent:.*",
        r"\bto:.*",
        r"\bsubject:.*",
        r"-----original message-----.*",
    ]

    for p in patterns:
        text = re.split(p, text, flags=re.IGNORECASE | re.DOTALL)[0]

    text = re.sub(r"\s+", " ", text).strip()
    return text
