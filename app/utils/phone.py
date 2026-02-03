import re

def extract_phone(text: str):
    if not text:
        return None

    match = re.search(r'(\+?\d{10,15})', text)
    return match.group(1) if match else None
