from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timedelta

from app.db.base import Base


class OAuthState(Base):
    __tablename__ = "oauth_states"

    id = Column(Integer, primary_key=True)
    state = Column(String(100), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)

    @staticmethod
    def expiry(minutes: int = 10):
        return datetime.utcnow() + timedelta(minutes=minutes)
    
