from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import Base
from datetime import datetime

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)

    proposal_id = Column(Integer, ForeignKey("proposals.id"))

    #  THIS IS THE IMPORTANT CHANGE
    reply_id = Column(Integer, ForeignKey("replies.id"), unique=True)

    meet_link = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
