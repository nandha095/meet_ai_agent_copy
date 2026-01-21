from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from app.db.base import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proposal_id = Column(Integer, ForeignKey("proposals.id"))
    reply_id = Column(Integer, ForeignKey("replies.id"), unique=True)

    meet_link = Column(String(2048), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
