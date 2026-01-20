from app.email_provider.gmail_provider import GmailProvider
from app.email_provider.outlook_provider import OutlookProvider


def get_email_provider(provider: str):
    """
    provider: 'google' or 'outlook'
    """
    if provider == "outlook":
        print("📤 Using OutlookProvider")
        return OutlookProvider()

    print("📤 Using GmailProvider")
    return GmailProvider()
