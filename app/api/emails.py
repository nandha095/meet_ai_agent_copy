from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import UploadFile, File, Form, HTTPException, Depends
from app.api.schemas import ProposalEmailRequest
from app.db.deps import get_db
from app.models.proposal import Proposal
from app.models.user import User
from app.api.auth import get_current_user
from typing import List
from app.email_provider.factory import get_email_provider
from app.models.google_token import GoogleToken
from app.models.outlook_token import OutlookToken

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
            "created_at": p.created_at
        }
        for p in proposals
    ]
