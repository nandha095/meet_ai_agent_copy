from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Primary login email (can be Gmail OR Outlook)
    email = Column(String(255), unique=True, index=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Which provider is ACTIVE for sending emails
    # must be "google" or "outlook"
    email_provider = Column(
        String(20),
        nullable=False,
        default="google"
    )

    # Actual Outlook sender address (filled after OAuth)
    outlook_email = Column(
        String(255),
        nullable=True
    )
