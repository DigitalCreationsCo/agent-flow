from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class SubscriptionStatus(str, Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    PAUSED = "paused"


class SubscriptionCreate(BaseModel):
    """Create subscription schema."""

    cancel_at: str | None = Field(default=None, description="Timestamp of when the subscription will be canceled")
    cancel_at_period_end: bool | None = Field(
        default=None, description="Whether the subscription will be canceled at the end of the period"
    )
    canceled_at: str | None = Field(default=None, description="Timestamp of when the subscription was canceled")
    created: str = Field(..., description="Timestamp of when the subscription was created")
    current_period_end: str = Field(..., description="End of the current subscription period")
    current_period_start: str = Field(..., description="Start of the current subscription period")
    ended_at: str | None = Field(default=None, description="Timestamp of when the subscription ended")
    id: str = Field(..., description="Unique identifier for the subscription")
    stripe_metadata: dict[str, Any] | None = Field(
        default=None, description="Set of key-value pairs for storing additional information"
    )
    price_id: str | None = Field(default=None, description="ID of the price associated with this subscription")
    quantity: int | None = Field(default=None, description="Quantity of the subscribed product")
    status: SubscriptionStatus = Field(..., description="Current status of the subscription")
    trial_end: str | None = Field(default=None, description="End date of the trial period")
    trial_start: str | None = Field(default=None, description="Start date of the trial period")
    user_id: str = Field(..., description="ID of the user who owns this subscription")

    @validator("created", "current_period_end", "current_period_start")
    def validate_timestamps(cls, v):
        """Validate timestamp strings."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError("Invalid timestamp format. Expected ISO format.")

    @validator("cancel_at", "canceled_at", "ended_at", "trial_end", "trial_start")
    def validate_optional_timestamps(cls, v):
        """Validate optional timestamp strings."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
                return v
            except ValueError:
                raise ValueError("Invalid timestamp format. Expected ISO format.")
        return v

    @validator("quantity")
    def validate_quantity(cls, v):
        """Validate quantity is positive if provided."""
        if v is not None and v < 1:
            raise ValueError("Quantity must be positive")
        return v

    @validator("user_id")
    def validate_user_id(cls, v):
        """Validate user_id is not empty."""
        if not v.strip():
            raise ValueError("user_id cannot be empty")
        return v


class SubscriptionRead(SubscriptionCreate):
    """Read subscription schema."""


class SubscriptionUpdate(BaseModel):
    """Update subscription schema."""

    cancel_at: str | None = None
    cancel_at_period_end: bool | None = None
    quantity: int | None = None
    status: SubscriptionStatus | None = None

    @validator("cancel_at")
    def validate_cancel_at(cls, v):
        """Validate cancel_at timestamp if provided."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
                return v
            except ValueError:
                raise ValueError("Invalid timestamp format. Expected ISO format.")
        return v

    @validator("quantity")
    def validate_quantity(cls, v):
        """Validate quantity is positive if provided."""
        if v is not None and v < 1:
            raise ValueError("Quantity must be positive")
        return v


class SubscriptionDelete(BaseModel):
    """Delete subscription schema."""

    id: str = Field(..., description="ID of the subscription to delete")
