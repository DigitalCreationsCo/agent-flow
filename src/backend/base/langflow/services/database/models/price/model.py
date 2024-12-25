from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Optional
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

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
    interval: Optional[PriceInterval] = None
    interval_count: Optional[int] = None
    trial_period_days: Optional[int] = None
    
    # Status
    is_active: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Additional data
    stripe_metadata: Dict[str, str] = Field(default_factory=dict, sa_type=JSON)
    
    # Relationships
    product: "ProductTable" = Relationship(back_populates="prices")

    class Config:
        arbitrary_types_allowed = True 