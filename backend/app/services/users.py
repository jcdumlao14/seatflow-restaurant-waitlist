from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import hash_password, normalize_email


ALLOWED_STAFF_ROLES = {
    "manager",
    "staff",
}


def create_restaurant_user(
    db: Session,
    restaurant_id: int,
    email: str,
    password: str,
    role: str,
) -> User:

    email = normalize_email(email)

    if role not in ALLOWED_STAFF_ROLES:
        raise ValueError(
            "User role must be manager or staff"
        )

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise ValueError(
            "Email is already registered"
        )

    user = User(
        restaurant_id=restaurant_id,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def list_restaurant_users(
    db: Session,
    restaurant_id: int,
) -> list[User]:

    return list(
        db.scalars(
            select(User)
            .where(
                User.restaurant_id == restaurant_id
            )
            .order_by(User.id)
        ).all()
    )


def update_user_role(
    db: Session,
    restaurant_id: int,
    user_id: int,
    role: str,
) -> User | None:

    if role not in ALLOWED_STAFF_ROLES:
        raise ValueError(
            "User role must be manager or staff"
        )

    user = db.scalar(
        select(User).where(
            User.id == user_id,
            User.restaurant_id == restaurant_id,
        )
    )

    if user is None:
        return None

    if user.role == "owner":
        raise ValueError(
            "Owner role cannot be changed"
        )

    user.role = role

    db.commit()
    db.refresh(user)

    return user
