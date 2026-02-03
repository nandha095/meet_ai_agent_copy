import re


def extract_phone(text: str) -> str | None:
    """
    Extract phone number from free text.
    Supports:
    - 9345649544
    - +919345649544
    - 93456 49544
    """
    if not text:
        return None

    match = re.search(r'(\+?\d[\d\s\-]{8,})', text)
    if not match:
        return None

    phone = match.group(1)
    phone = re.sub(r'\D', '', phone)  # keep digits only

    # If Indian 10-digit number
    if len(phone) == 10:
        return phone

    # If country code already present
    if len(phone) > 10:
        return "+" + phone

    return None


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to E.164 format (India)
    9345649544 -> +919345649544
    """
    if not phone:
        return phone

    phone = phone.strip().replace(" ", "").replace("-", "")

    if phone.startswith("+"):
        return phone

    if len(phone) == 10:
        return "+91" + phone

    return phone
