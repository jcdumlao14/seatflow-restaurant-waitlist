from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth_dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.waitlist import (
    WaitlistCreate,
    WaitlistResponse,
)
from app.services.websocket import broadcast_waitlist_update
from app.services.waitlist import (
    CANCELLED,
    NO_SHOW,
    SEATED,
    call_next,
    create_waitlist_entry,
    get_statistics,
    get_waitlist,
    update_entry_status,
)


router = APIRouter(
    prefix="/api/waitlist",
    tags=["Waitlist"],
)


@router.get(
    "",
    response_model=list[WaitlistResponse],
)
def get_waitlist_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_waitlist(
        db,
        current_user.restaurant_id,
    )


@router.post(
    "",
    response_model=WaitlistResponse,
    status_code=201,
)
async def add_to_waitlist(
    payload: WaitlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = create_waitlist_entry(
        db,
        current_user.restaurant_id,
        payload.customer_name,
        payload.phone,
        payload.party_size,
    )

    await broadcast_waitlist_update(
        current_user.restaurant_id,
        "created",
        entry.id,
    )

    return entry


@router.post(
    "/call-next",
    response_model=WaitlistResponse,
)
async def call_next_party(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = call_next(
        db,
        current_user.restaurant_id,
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="No customers are currently waiting",
        )

    await broadcast_waitlist_update(
        current_user.restaurant_id,
        "called",
        entry.id,
    )

    return entry


@router.patch(
    "/{entry_id}/status",
    response_model=WaitlistResponse,
)
async def update_status(
    entry_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        entry = update_entry_status(
            db,
            current_user.restaurant_id,
            entry_id,
            status,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found",
        )

    await broadcast_waitlist_update(
        current_user.restaurant_id,
        "status_changed",
        entry.id,
    )

    return entry


@router.post(
    "/{entry_id}/seat",
    response_model=WaitlistResponse,
)
async def seat_party(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = update_entry_status(
        db,
        current_user.restaurant_id,
        entry_id,
        SEATED,
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found",
        )

    await broadcast_waitlist_update(
        current_user.restaurant_id,
        "seated",
        entry.id,
    )

    return entry


@router.post(
    "/{entry_id}/cancel",
    response_model=WaitlistResponse,
)
async def cancel_party(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = update_entry_status(
        db,
        current_user.restaurant_id,
        entry_id,
        CANCELLED,
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found",
        )

    await broadcast_waitlist_update(
        current_user.restaurant_id,
        "cancelled",
        entry.id,
    )

    return entry


@router.post(
    "/{entry_id}/no-show",
    response_model=WaitlistResponse,
)
async def no_show_party(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = update_entry_status(
        db,
        current_user.restaurant_id,
        entry_id,
        NO_SHOW,
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found",
        )

    await broadcast_waitlist_update(
        current_user.restaurant_id,
        "no_show",
        entry.id,
    )

    return entry


@router.get(
    "/statistics/summary",
)
def waitlist_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_statistics(
        db,
        current_user.restaurant_id,
    )
