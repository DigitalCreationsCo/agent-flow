from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


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
    interval: Optional[PriceInterval] = Field(None, description="Billing interval for recurring prices")
    interval_count: Optional[int] = Field(None, description="Number of intervals between billings")
    trial_period_days: Optional[int] = Field(None, description="Number of trial days")
    is_active: bool = Field(default=True, description="Whether the price is active")
    stripe_metadata: Optional[Dict[str, Any]] = Field(None, description="additional Stripe metadata")


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
    description: Optional[str] = Field(None, description="Product description")
    is_active: bool = Field(default=True, description="Whether the product is active")
    image: Optional[str] = Field(None, description="URL to product image")
    stripe_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProductCreate(ProductBase):
    """Create product schema."""
    pass


class ProductRead(ProductBase):
    """Read product schema."""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    prices: List[PriceRead] = Field(default_factory=list, description="Associated prices")


class ProductUpdate(BaseModel):
    """Update product schema."""
    name: Optional[str] = Field(None, description="Name of the product")
    description: Optional[str] = Field(None, description="Product description")
    image: Optional[str] = Field(None, description="URL to product image")


class PriceUpdate(BaseModel):
    """Update price schema."""
    unit_amount: Optional[int] = Field(None, description="Amount in cents")
