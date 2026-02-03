from datetime import timedelta
from app.models.meeting import Meeting


def find_alternative_slots(
    db,
    user_id: int,
    base_start,
    duration_minutes: int = 30,
    max_options: int = 3,
):
    alternatives = []

    for i in range(1, 7):  # try next 3 hours
        start = base_start + timedelta(minutes=30 * i)
        end = start + timedelta(minutes=duration_minutes)

        conflict = (
            db.query(Meeting)
            .filter(
                Meeting.user_id == user_id,
                Meeting.start_time < end,
                Meeting.end_time > start,
            )
            .first()
        )

        if not conflict:
            alternatives.append(start)

        if len(alternatives) >= max_options:
            break

    return alternatives
