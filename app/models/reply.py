from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from app.db.base import Base
from sqlalchemy import Boolean

class Reply(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True)
    gmail_message_id = Column(String, unique=True, index=True)
    sender = Column(String)
    subject = Column(String)
    body = Column(String)

    meeting_interest = Column(Boolean, default=False)
    confidence = Column(Float, default=0.0)

    
    waiting_for_schedule = Column(Boolean, default=False)