from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas import ProposalEmailRequest
from app.services.email_service import send_proposal_email
from app.db.deps import get_db
from app.models.proposal import Proposal

router = APIRouter()

@router.post("/send-proposal")
def send_proposal(
    payload: ProposalEmailRequest,
    db: Session = Depends(get_db)
):
    subject = "Project Proposal"
    body = """
    <h3>Hello,</h3>
    <p>We would like to propose a project collaboration.</p>
    <p>Please let us know if you'd like to schedule a meeting.</p>
    <br>
    <p>Regards,<br>Nandhakumar</p>
    """

    # Send email
    send_proposal_email(
        to_email=payload.email,
        subject=subject,
        body=body
    )

    # Save to DB
    proposal = Proposal(
        client_email=payload.email,
        subject=subject,
        body=body
    )
    db.add(proposal)
    db.commit()

    return {"message": "Proposal sent and saved"}
