from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import Field
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from langflow.services.database.models.product.model import ProductTable
    from langflow.services.database.models.user import User


def utc_now():
    return datetime.now(timezone.utc)


class SubscriptionStatus(str, Enum):
    """Subscription status enum."""

    TRIALING = "trialing"
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"


class PlanType(str, Enum):
    """Plan type enum."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionTable(SQLModel, table=True):
    """Database model for subscriptions."""

    __tablename__ = "subscription"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    product_id: UUID = Field(foreign_key="product.id", index=True)
    external_subscription_id: str | None = Field(default=None, index=True)

    # Status and period
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE, index=True)
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = Field(default=False)

    # Trial information
    trial_start: datetime | None = None
    trial_end: datetime | None = None

    # Usage tracking
    api_calls_used: int = Field(default=0)
    storage_used: int = Field(default=0)  # in MB

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    canceled_at: datetime | None = None
    ended_at: datetime | None = None

    # Additional data
    # metadata: dict = Field(default_factory=dict)
    payment_status: str | None = None
    last_payment_date: datetime | None = None
    next_payment_date: datetime | None = None

    # Relationships
    user: Optional["User"] = Relationship(back_populates="subscriptions")
    product: "ProductTable" = Relationship(back_populates="subscriptions")

    class Config:
        arbitrary_types_allowed = True

    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status in [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        ] and self.current_period_end > datetime.now(timezone.utc)

    def has_available_api_calls(self) -> bool:
        """Check if subscription has available API calls."""
        if self.api_calls_limit is None:
            return True
        return self.api_calls_used < self.api_calls_limit

    def has_available_storage(self) -> bool:
        """Check if subscription has available storage."""
        if self.storage_limit is None:
            return True
        return self.storage_used < self.storage_limit
