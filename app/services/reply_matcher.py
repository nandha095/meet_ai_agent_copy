from sqlalchemy.orm import Session
from app.models.proposal import Proposal


def find_matching_proposal(db: Session, subject: str):
    """
    Try to match reply to proposal using subject
    """
    clean_subject = subject.replace("Re:", "").strip()

    return (
        db.query(Proposal)
        .filter(Proposal.subject.ilike(f"%{clean_subject}%"))
        .first()
    )
