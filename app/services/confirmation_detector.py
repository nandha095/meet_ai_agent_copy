def is_confirmation_reply(text: str) -> bool:
    t = text.lower()

    confirm_phrases = [
        "yes confirm",
        "confirmed",
        "yes that works",
        "okay confirmed",
        "go ahead",
        "looks good"
    ]

    return any(p in t for p in confirm_phrases)
