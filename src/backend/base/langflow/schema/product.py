from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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


class PriceBase(BaseModel):
    """Base price schema."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name of the price")
    type: PriceType = Field(..., description="Type of price (one-time or recurring)")
    unit_amount: int = Field(..., description="Amount in cents")
    currency: str = Field(default="usd", description="Currency code")
    interval: PriceInterval | None = Field(None, description="Billing interval for recurring prices")
    interval_count: int | None = Field(None, description="Number of intervals between billings")
    trial_period_days: int | None = Field(None, description="Number of trial days")
    is_active: bool = Field(default=True, description="Whether the price is active")
    stripe_metadata: dict[str, Any] | None = Field(None, description="additional Stripe metadata")


class PriceCreate(PriceBase):
    """Create price schema."""

    product_id: str = Field(..., description="ID of the associated product")


class PriceRead(PriceBase):
    """Read price schema."""

    product_id: str = Field(..., description="ID of the associated product")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ProductBase(BaseModel):
    """Base product schema."""

    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name of the product")
    description: str | None = Field(None, description="Product description")
    is_active: bool = Field(default=True, description="Whether the product is active")
    image: str | None = Field(None, description="URL to product image")
    stripe_metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class ProductCreate(ProductBase):
    """Create product schema."""


class ProductRead(ProductBase):
    """Read product schema."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    prices: list[PriceRead] = Field(default_factory=list, description="Associated prices")


class ProductUpdate(BaseModel):
    """Update product schema."""

    name: str | None = Field(None, description="Name of the product")
    description: str | None = Field(None, description="Product description")
    image: str | None = Field(None, description="URL to product image")


class PriceUpdate(BaseModel):
    """Update price schema."""

    unit_amount: int | None = Field(None, description="Amount in cents")
