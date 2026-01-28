from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from app.db.base import Base

class Reply(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)

    gmail_message_id = Column(String(255), unique=True, index=True)
    sender = Column(String(255))
    subject = Column(String(255))
    body = Column(String(5000))

    meeting_interest = Column(Boolean, default=False)
    confidence = Column(Float, default=0.0)
    llm_attempted = Column(Boolean, default=False)
    
