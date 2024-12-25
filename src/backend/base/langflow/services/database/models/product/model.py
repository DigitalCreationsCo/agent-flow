from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, Optional, List

from sqlalchemy import JSON, Column
from sqlmodel import Relationship, SQLModel, Field
from enum import Enum   

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
    description: Optional[str] = None
    price_id: Optional[str] = Field(default=None, index=True)  # For payment processor reference
    unit_amount: int = Field(default=0)  # Price in cents
    currency: str = Field(default="usd")
    # Features and limits
    api_calls_limit: Optional[int] = None
    storage_limit: Optional[int] = None  # in MB
    concurrent_runs_limit: Optional[int] = None
    
    # Status
    is_active: bool = Field(default=True)
    
    # Trial settings
    trial_days: Optional[int] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Additional data
    stripe_metadata: Dict[str, str] = Field(default_factory=dict, sa_type=JSON)

    # Relationships
    subscriptions: list["SubscriptionTable"] = Relationship(back_populates="product")
    prices: List["PriceTable"] = Relationship(back_populates="product")

    class Config:
        arbitrary_types_allowed = True 