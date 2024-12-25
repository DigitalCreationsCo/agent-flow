from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum
from pydantic import field_validator
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.user import User
    from langflow.services.database.models.product.model import ProductTable

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
    external_subscription_id: Optional[str] = Field(default=None, index=True)
    
    # Status and period
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE, index=True)
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = Field(default=False)
    
    # Trial information
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    
    # Usage tracking
    api_calls_used: int = Field(default=0)
    storage_used: int = Field(default=0)  # in MB
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    canceled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    
    # Additional data
    # metadata: dict = Field(default_factory=dict)
    payment_status: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    next_payment_date: Optional[datetime] = None

    # Relationships
    user: Optional["User"] = Relationship(back_populates="subscriptions")
    product: "ProductTable" = Relationship(back_populates="subscriptions")

    class Config:
        arbitrary_types_allowed = True

    def is_active(self) -> bool:
        """Check if subscription is active."""
        return (
            self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
            and self.current_period_end > datetime.now(timezone.utc)
        )
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

