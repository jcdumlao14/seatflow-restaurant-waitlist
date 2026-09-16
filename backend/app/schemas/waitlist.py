from datetime import datetime

from pydantic import BaseModel, Field


class WaitlistCreate(BaseModel):
    customer_name: str = Field(
        min_length=1,
        max_length=100,
    )

    phone: str = Field(
        min_length=1,
        max_length=30,
    )

    party_size: int = Field(
        ge=1,
        le=50,
    )


class WaitlistResponse(BaseModel):
    id: int

    restaurant_id: int

    customer_name: str

    phone: str

    party_size: int

    status: str

    estimated_wait_minutes: int

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
