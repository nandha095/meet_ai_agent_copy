from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from datetime import datetime
from app.db.base import Base


class OutlookToken(Base):
    __tablename__ = "outlook_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    access_token = Column(Text)
    refresh_token = Column(Text)

    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
