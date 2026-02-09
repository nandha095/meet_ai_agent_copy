from datetime import datetime

from app.db.session import SessionLocal
from app.models.token_blacklist import TokenBlacklist


def cleanup_expired_tokens() -> int:
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        deleted = (
            db.query(TokenBlacklist)
            .filter(TokenBlacklist.expires_at < now)
            .delete(synchronize_session=False)
        )
        db.commit()
        return deleted or 0
    finally:
        db.close()
