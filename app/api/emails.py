from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import ProposalEmailRequest
from app.db.deps import get_db
from app.models.proposal import Proposal
from app.models.user import User
from app.api.auth import get_current_user

from app.email_provider.factory import get_email_provider
from app.models.google_token import GoogleToken
from app.models.outlook_token import OutlookToken

router = APIRouter(
    prefix="/emails",
    tags=["Emails"]
)

@router.post("/send-proposal")
def send_proposal(
    payload: ProposalEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    provider_name = payload.provider.lower()

    if provider_name not in ("google", "outlook"):
        raise HTTPException(400, "Invalid provider")

    # 🔐 Ensure provider is connected
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

    provider = get_email_provider(provider_name)

    # ✅ SEND EMAIL
    provider.send_email(
        db=db,
        user_id=current_user.id,
        to_email=payload.email,
        subject=payload.subject,
        body_html=payload.body,
        body_text=payload.body,
    )

    # ✅ SAVE PROPOSAL (SOURCE OF TRUTH)
    proposal = Proposal(
        user_id=current_user.id,
        client_email=payload.email.lower(),
        subject=payload.subject,
        body=payload.body,
        status="SENT",
        provider=provider_name,
    )

    db.add(proposal)
    db.commit()

    return {
        "message": f"Proposal sent via {provider_name}",
        "provider": provider_name
    }
