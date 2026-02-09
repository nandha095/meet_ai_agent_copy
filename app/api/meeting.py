from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import pytz

from app.db.deps import get_db
from app.models.meeting import Meeting
from app.services.meeting_email_service import send_meeting_link_email
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()
IST = pytz.timezone("Asia/Kolkata")

def to_ist_iso(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(IST).isoformat()


@router.post("/resend-email/{meeting_id}")
def resend_meeting_email(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    to_email = meeting.reply.sender.split("<")[-1].replace(">", "").strip()

    send_meeting_link_email(
        to_email=to_email,
        meet_link=meeting.meet_link,
        start_time=meeting.start_time,
        end_time=meeting.end_time
    )

    return {"message": "Meeting email resent successfully"}


@router.get("/next")
def next_meeting(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.utcnow()
    meeting = (
        db.query(Meeting)
        .filter(Meeting.user_id == current_user.id)
        .filter(Meeting.start_time >= now)
        .order_by(Meeting.start_time.asc())
        .first()
    )
    if not meeting:
        return {"meeting": None}

    return {
        "meeting": {
            "id": meeting.id,
            "start_time": to_ist_iso(meeting.start_time),
            "end_time": to_ist_iso(meeting.end_time),
            "meet_link": meeting.meet_link
        }
    }
