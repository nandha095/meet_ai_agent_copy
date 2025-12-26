from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.reply_processor import process_replies

router = APIRouter()

@router.get("/fetch")
def fetch_replies(db: Session = Depends(get_db)):
    process_replies(db)
    return {"status": "processed"}
