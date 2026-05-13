from app.services.new import celery
from app.db.session import SessionLocal
from app.models.user import User
from app.services.reply_processor import process_replies
from app.services.token_cleanup import cleanup_expired_tokens


@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def process_replies_task(self, user_id: int):
    db = SessionLocal()
    try:
        process_replies(db, user_id)
    finally:
        db.close()


@celery.task
def dispatch_reply_processing():
    db = SessionLocal()
    try:
        users = db.query(User).all()

        if not users:
            print("No users found. Skipping reply processing.")
            return

        for user in users:
            print(f"Queueing reply processing for user: {user.email}")
            process_replies_task.delay(user.id)
    finally:
        db.close()


@celery.task
def cleanup_expired_tokens_task():
    cleanup_expired_tokens()

