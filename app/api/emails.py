from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.responses import Response
import csv
import io
import pytz
from fastapi import UploadFile, File, Form, HTTPException, Depends
from app.api.schemas import ProposalEmailRequest
from app.db.deps import get_db
from app.models.proposal import Proposal
from app.models.user import User
from app.models.meeting import Meeting
from sqlalchemy import desc
from app.api.auth import get_current_user
from typing import List
from app.email_provider.factory import get_email_provider
from app.models.google_token import GoogleToken
from app.models.outlook_token import OutlookToken

IST = pytz.timezone("Asia/Kolkata")

def to_ist_iso(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(IST).isoformat()

router = APIRouter(
    prefix="/proposals",
    tags=["Proposals"]
)

router = APIRouter(
    prefix="/emails",
    tags=["Emails"]
)


@router.post("/send-proposal")
def send_proposal(
    email: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    provider: str = Form(...),
    attachments: list[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    required_subject = "Project Proposal"
    provider_name = provider.lower()

    if provider_name not in ("google", "outlook"):
        raise HTTPException(400, "Invalid provider")

    # Ensure provider is connected
    if provider_name == "google":
        token = db.query(GoogleToken).filter(
            GoogleToken.user_id == current_user.id
        ).first()
        if not token:
            raise HTTPException(400, "Google not connected")

    if provider_name == "outlook":
        token = db.query(OutlookToken).filter(
            OutlookToken.user_id == current_user.id
        ).first()
        if not token:
            raise HTTPException(400, "Outlook not connected")

    provider_instance = get_email_provider(provider_name)

    # Enforce standard subject line
    subject = required_subject

    #  SEND EMAIL WITH ATTACHMENTS
    provider_instance.send_email(
        db=db,
        user_id=current_user.id,
        to_email=email,
        subject=subject,
        body_html=body,
        body_text=body,
        attachments=attachments
    )

    #  SAVE PROPOSAL
    proposal = Proposal(
        user_id=current_user.id,
        client_email=email.lower(),
        subject=subject,
        body=body,
        status="SENT",
        provider=provider_name,
    )

    db.add(proposal)
    db.commit()

    return {
        "message": f"Proposal sent via {provider_name}",
        "provider": provider_name
    }

@router.get("/")
def get_my_proposals(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    proposals = (
        db.query(Proposal)
        .filter(Proposal.user_id == current_user.id)
        .order_by(Proposal.created_at.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "client_email": p.client_email,
            "subject": p.subject,
            "status": p.status,
            "provider": p.provider,
            "created_at": to_ist_iso(p.created_at)
        }
        for p in proposals
    ]


@router.get("/paged")
def get_my_proposals_paged(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    page = max(page, 1)
    size = min(max(size, 1), 50)
    total = (
        db.query(func.count(Proposal.id))
        .filter(Proposal.user_id == current_user.id)
        .scalar()
    )
    proposals = (
        db.query(Proposal)
        .filter(Proposal.user_id == current_user.id)
        .order_by(Proposal.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return {
        "items": [
            {
                "id": p.id,
                "client_email": p.client_email,
                "subject": p.subject,
                "status": p.status,
                "provider": p.provider,
                "created_at": to_ist_iso(p.created_at)
            }
            for p in proposals
        ],
        "total": total or 0,
        "page": page,
        "size": size
    }


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    proposals_sent = (
        db.query(func.count(Proposal.id))
        .filter(Proposal.user_id == current_user.id)
        .scalar()
    )

    meetings_scheduled = (
        db.query(func.count(Meeting.id))
        .filter(Meeting.user_id == current_user.id)
        .scalar()
    )

    return {
        "proposals_sent": proposals_sent or 0,
        "meetings_scheduled": meetings_scheduled or 0
    }


@router.get("/activity")
def get_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    proposals = (
        db.query(Proposal)
        .filter(Proposal.user_id == current_user.id)
        .order_by(desc(Proposal.created_at))
        .limit(10)
        .all()
    )

    meetings = (
        db.query(Meeting)
        .filter(Meeting.user_id == current_user.id)
        .order_by(desc(Meeting.created_at))
        .limit(10)
        .all()
    )

    activity = []
    for p in proposals:
        activity.append({
            "type": "proposal",
            "id": p.id,
            "title": f"Proposal sent to {p.client_email}",
            "status": p.status,
            "provider": p.provider,
            "created_at": to_ist_iso(p.created_at)
        })

    for m in meetings:
        activity.append({
            "type": "meeting",
            "id": m.id,
            "title": "Meeting scheduled",
            "status": "MEETING_SCHEDULED",
            "provider": None,
            "created_at": to_ist_iso(m.created_at),
            "start_time": to_ist_iso(m.start_time),
            "end_time": to_ist_iso(m.end_time),
            "meet_link": m.meet_link
        })

    activity.sort(key=lambda x: x["created_at"], reverse=True)

    return activity[:15]


@router.get("/activity-paged")
def get_activity_paged(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    page = max(page, 1)
    size = min(max(size, 1), 50)

    proposals = (
        db.query(Proposal)
        .filter(Proposal.user_id == current_user.id)
        .order_by(desc(Proposal.created_at))
        .all()
    )
    meetings = (
        db.query(Meeting)
        .filter(Meeting.user_id == current_user.id)
        .order_by(desc(Meeting.created_at))
        .all()
    )

    activity = []
    for p in proposals:
        activity.append({
            "type": "proposal",
            "id": p.id,
            "title": f"Proposal sent to {p.client_email}",
            "status": p.status,
            "provider": p.provider,
            "created_at": to_ist_iso(p.created_at)
        })
    for m in meetings:
        activity.append({
            "type": "meeting",
            "id": m.id,
            "title": "Meeting scheduled",
            "status": "MEETING_SCHEDULED",
            "provider": None,
            "created_at": to_ist_iso(m.created_at),
            "start_time": to_ist_iso(m.start_time),
            "end_time": to_ist_iso(m.end_time),
            "meet_link": m.meet_link
        })

    activity.sort(key=lambda x: x["created_at"], reverse=True)
    total = len(activity)
    start = (page - 1) * size
    end = start + size

    return {
        "items": activity[start:end],
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/export")
def export_proposals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    proposals = (
        db.query(Proposal)
        .filter(Proposal.user_id == current_user.id)
        .order_by(Proposal.created_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "client_email", "subject", "status", "provider", "created_at"])
    for p in proposals:
        writer.writerow([
            p.id,
            p.client_email,
            p.subject,
            p.status,
            p.provider,
            p.created_at.isoformat() if p.created_at else ""
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=proposals.csv"}
    )
