import os
import re
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.models.user import User


SECRET_KEY = os.getenv(
    "SEATFLOW_SECRET_KEY",
    "seatflow-development-secret-change-in-production",
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user.id),
        "restaurant_id": user.restaurant_id,
        "role": user.role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def normalize_email(email: str) -> str:
    return email.strip().lower()


def make_slug(name: str) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        name.lower(),
    ).strip("-")

    return slug or "restaurant"


def unique_slug(db: Session, name: str) -> str:
    base_slug = make_slug(name)
    slug = base_slug
    counter = 2

    while db.scalar(
        select(Restaurant).where(Restaurant.slug == slug)
    ) is not None:
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def register_owner(
    db: Session,
    restaurant_name: str,
    email: str,
    password: str,
) -> tuple[Restaurant, User]:

    email = normalize_email(email)

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise ValueError("Email is already registered")

    if len(password) < 8:
        raise ValueError(
            "Password must be at least 8 characters"
        )

    restaurant = Restaurant(
        name=restaurant_name.strip(),
        slug=unique_slug(db, restaurant_name),
    )

    db.add(restaurant)
    db.flush()

    user = User(
        restaurant_id=restaurant.id,
        email=email,
        password_hash=hash_password(password),
        role="owner",
        is_active=True,
    )

    db.add(user)
    db.commit()

    db.refresh(restaurant)
    db.refresh(user)

    return restaurant, user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:

    email = normalize_email(email)

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user
