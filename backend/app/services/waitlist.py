from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.waitlist import WaitlistEntry


WAITING = "waiting"
NOTIFIED = "notified"
SEATED = "seated"
CANCELLED = "cancelled"
NO_SHOW = "no_show"

VALID_STATUSES = {
    WAITING,
    NOTIFIED,
    SEATED,
    CANCELLED,
    NO_SHOW,
}


def calculate_wait_minutes(
    db: Session,
    restaurant_id: int,
) -> int:

    waiting_count = db.scalar(
        select(func.count())
        .select_from(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id,
            WaitlistEntry.status == WAITING,
        )
    )

    return max(
        10,
        (waiting_count or 0) * 15,
    )


def create_waitlist_entry(
    db: Session,
    restaurant_id: int,
    customer_name: str,
    phone: str,
    party_size: int,
) -> WaitlistEntry:

    waiting_count = db.scalar(
        select(func.count())
        .select_from(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id,
            WaitlistEntry.status == WAITING,
        )
    )

    entry = WaitlistEntry(
        restaurant_id=restaurant_id,
        customer_name=customer_name,
        phone=phone,
        party_size=party_size,
        status=WAITING,
        estimated_wait_minutes=max(
            10,
            (waiting_count or 0) * 15,
        ),
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry


def get_waitlist(
    db: Session,
    restaurant_id: int,
) -> list[WaitlistEntry]:

    return list(
        db.scalars(
            select(WaitlistEntry)
            .where(
                WaitlistEntry.restaurant_id == restaurant_id
            )
            .order_by(WaitlistEntry.created_at)
        ).all()
    )


def call_next(
    db: Session,
    restaurant_id: int,
) -> WaitlistEntry | None:

    entry = db.scalar(
        select(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id,
            WaitlistEntry.status == WAITING,
        )
        .order_by(WaitlistEntry.created_at)
    )

    if entry is None:
        return None

    entry.status = NOTIFIED

    db.commit()
    db.refresh(entry)

    return entry


def update_entry_status(
    db: Session,
    restaurant_id: int,
    entry_id: int,
    status: str,
) -> WaitlistEntry | None:

    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status: {status}"
        )

    entry = db.scalar(
        select(WaitlistEntry).where(
            WaitlistEntry.id == entry_id,
            WaitlistEntry.restaurant_id == restaurant_id,
        )
    )

    if entry is None:
        return None

    entry.status = status

    db.commit()
    db.refresh(entry)

    return entry


def get_statistics(
    db: Session,
    restaurant_id: int,
) -> dict[str, int | float]:

    total = db.scalar(
        select(func.count())
        .select_from(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id
        )
    ) or 0

    waiting = db.scalar(
        select(func.count())
        .select_from(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id,
            WaitlistEntry.status == WAITING,
        )
    ) or 0

    notified = db.scalar(
        select(func.count())
        .select_from(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id,
            WaitlistEntry.status == NOTIFIED,
        )
    ) or 0

    seated = db.scalar(
        select(func.count())
        .select_from(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id,
            WaitlistEntry.status == SEATED,
        )
    ) or 0

    cancelled = db.scalar(
        select(func.count())
        .select_from(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id,
            WaitlistEntry.status == CANCELLED,
        )
    ) or 0

    no_show = db.scalar(
        select(func.count())
        .select_from(WaitlistEntry)
        .where(
            WaitlistEntry.restaurant_id == restaurant_id,
            WaitlistEntry.status == NO_SHOW,
        )
    ) or 0

    return {
        "total": total,
        "waiting": waiting,
        "notified": notified,
        "seated": seated,
        "cancelled": cancelled,
        "no_show": no_show,
    }
