from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.meeting import Meeting
from app.services.meeting_email_service import send_meeting_link_email

router = APIRouter()


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
