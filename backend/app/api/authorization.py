from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.auth_dependencies import get_current_user
from app.models.user import User


def require_roles(*allowed_roles: str) -> Callable:
    """
    Restrict an endpoint to specific user roles.
    """

    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return dependency
