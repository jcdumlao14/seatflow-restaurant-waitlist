from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth_dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.auth import (
    authenticate_user,
    create_access_token,
    register_owner,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


def user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        restaurant_id=user.restaurant_id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        restaurant, user = register_owner(
            db,
            payload.restaurant_name,
            str(payload.email),
            payload.password,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return AuthResponse(
        access_token=create_access_token(user),
        user=user_response(user),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        str(payload.email),
        payload.password,
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return AuthResponse(
        access_token=create_access_token(user),
        user=user_response(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    return user_response(current_user)
