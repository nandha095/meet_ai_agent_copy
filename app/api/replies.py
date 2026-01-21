from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.reply_processor import process_replies
from app.api.auth import get_current_user
from app.models.user import User
from app.models.proposal import Proposal

router = APIRouter()

@router.get("/fetch")
def fetch_replies(db: Session = Depends(get_db)):
    process_replies(db)
    return {"status": "processed"}


# @router.get("/replies")
# def fetch_replies(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     # 1️ Process incoming replies
#     process_replies(db, current_user.id)

#     # 2️ Fetch updated proposals
#     proposals = (
#         db.query(Proposal)
#         .filter(Proposal.user_id == current_user.id)
#         .order_by(Proposal.created_at.desc())
#         .all()
#     )

#     # 3️ Serialize response
#     return [
#         {
#             "id": p.id,
#             "client_email": p.client_email,
#             "subject": p.subject,
#             "provider": p.provider,
#             "status": p.status,
#             "created_at": p.created_at,
#             "meeting_link": p.meeting.meet_link if p.meeting else None,
#         }
#         for p in proposals
#     ]