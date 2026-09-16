from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    role: str = Field(
        default="staff",
        pattern="^(manager|staff)$",
    )


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(
        pattern="^(manager|staff)$",
    )


class UserResponse(BaseModel):
    id: int
    restaurant_id: int
    email: str
    role: str
    is_active: bool
