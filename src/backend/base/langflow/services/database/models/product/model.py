from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from langflow.services.database.models.price.model import PriceTable
    from langflow.services.database.models.subscription.model import SubscriptionTable


class ProductType(str, Enum):
    """Product type enum."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ProductTable(SQLModel, table=True):
    """Database model for products/plans available in the platform."""

    __tablename__ = "product"

    id: str = Field(primary_key=True)
    name: str = Field(index=True, unique=True)
    type: ProductType = Field(default=ProductType.FREE)
    description: str | None = None
    price_id: str | None = Field(default=None, index=True)  # For payment processor reference
    unit_amount: int = Field(default=0)  # Price in cents
    currency: str = Field(default="usd")
    # Features and limits
    api_calls_limit: int | None = None
    storage_limit: int | None = None  # in MB
    concurrent_runs_limit: int | None = None

    # Status
    is_active: bool = Field(default=True)

    # Trial settings
    trial_days: int | None = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Additional data
    stripe_metadata: dict[str, str] = Field(default_factory=dict, sa_type=JSON)

    # Relationships
    subscriptions: list["SubscriptionTable"] = Relationship(back_populates="product")
    prices: list["PriceTable"] = Relationship(back_populates="product")

    class Config:
        arbitrary_types_allowed = True
