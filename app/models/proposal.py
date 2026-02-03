from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.db.base import Base

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    client_email = Column(String(255), index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(String(5000), nullable=False)
    status = Column(String(50), default="SENT")

    created_at = Column(DateTime, default=datetime.utcnow)
    
    provider = Column(String(20), nullable=False)  # "google" or "outlook"
    client_phone = Column(String, nullable=True)