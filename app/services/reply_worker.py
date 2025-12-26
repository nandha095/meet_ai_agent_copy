from app.db.session import SessionLocal
from app.services.reply_processor import process_replies

def run_reply_worker():
    db = SessionLocal()
    try:
        process_replies(db)
        print("✅ Background job: replies processed")
    except Exception as e:
        print("❌ Background job error:", e)
    finally:
        db.close()
