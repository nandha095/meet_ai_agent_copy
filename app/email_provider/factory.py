from app.email_provider.gmail_provider import GmailProvider
from app.email_provider.outlook_provider import OutlookProvider


def get_email_provider(provider: str):
    if provider == "gmail" or provider == "google":
        return GmailProvider()
    elif provider == "outlook":
        return OutlookProvider()
    else:
        raise ValueError(f"Unknown email provider: {provider}")
