from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.authorization import require_roles
from app.database import get_db
from app.models.user import User
from app.schemas.users import (
    UserCreateRequest,
    UserResponse,
    UserRoleUpdateRequest,
)
from app.services.users import (
    create_restaurant_user,
    list_restaurant_users,
    update_user_role,
)


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


def user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        restaurant_id=user.restaurant_id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )


@router.get(
    "",
    response_model=list[UserResponse],
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("owner", "manager")
    ),
):
    users = list_restaurant_users(
        db,
        current_user.restaurant_id,
    )

    return [
        user_response(user)
        for user in users
    ]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("owner")
    ),
):
    try:
        user = create_restaurant_user(
            db,
            current_user.restaurant_id,
            str(payload.email),
            payload.password,
            payload.role,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return user_response(user)


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
def change_user_role(
    user_id: int,
    payload: UserRoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("owner")
    ),
):
    try:
        user = update_user_role(
            db,
            current_user.restaurant_id,
            user_id,
            payload.role,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user_response(user)
