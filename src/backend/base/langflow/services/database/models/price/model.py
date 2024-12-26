from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from langflow.services.database.models.product.model import ProductTable


class PriceType(str, Enum):
    """Price type enum."""

    ONE_TIME = "one_time"
    RECURRING = "recurring"


class PriceInterval(str, Enum):
    """Price interval enum."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class PriceTable(SQLModel, table=True):
    """Database model for product prices."""

    __tablename__ = "price"

    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    type: PriceType
    product_id: str = Field(foreign_key="product.id", index=True)

    unit_amount: int  # Amount in cents
    currency: str = Field(default="usd")

    # Recurring price settings
    interval: PriceInterval | None = None
    interval_count: int | None = None
    trial_period_days: int | None = None

    # Status
    is_active: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Additional data
    stripe_metadata: dict[str, str] = Field(default_factory=dict, sa_type=JSON)

    # Relationships
    product: "ProductTable" = Relationship(back_populates="prices")

    class Config:
        arbitrary_types_allowed = True
