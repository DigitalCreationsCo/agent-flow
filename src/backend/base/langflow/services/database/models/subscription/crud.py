from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from langflow.schema.subscription import (
    SubscriptionRead,
    SubscriptionCreate,
    SubscriptionUpdate
)
from langflow.services.database.models.subscription.model import SubscriptionTable
from sqlmodel.sql.expression import SelectOfScalar

async def get_subscriptions(session: AsyncSession) -> list[SubscriptionRead]:
    """Get all subscriptions."""
    query: SelectOfScalar = select(SubscriptionTable)
    subscriptions = (await session.exec(query)).all()
    return [SubscriptionRead.model_validate(sub, from_attributes=True) for sub in subscriptions]

async def get_subscription(session: AsyncSession, subscription_id: UUID) -> SubscriptionRead | None:
    """Get a subscription by ID."""
    subscription = await session.get(SubscriptionTable, subscription_id)
    if subscription is None:
        return None
    return SubscriptionRead.model_validate(subscription, from_attributes=True)

async def create_subscription(
    session: AsyncSession, 
    subscription_create: SubscriptionCreate
) -> SubscriptionRead:
    """Create a new subscription."""
    subscription = SubscriptionTable(**subscription_create.model_dump())
    session.add(subscription)
    await session.commit()
    await session.refresh(subscription)
    return SubscriptionRead.model_validate(subscription, from_attributes=True)

async def update_subscription(
    session: AsyncSession,
    subscription_id: UUID,
    subscription_update: SubscriptionUpdate
) -> SubscriptionRead | None:
    """Update a subscription."""
    subscription = await session.get(SubscriptionTable, subscription_id)
    if subscription is None:
        return None
    
    update_data = subscription_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(subscription, key, value)
    
    session.add(subscription)
    await session.commit()
    await session.refresh(subscription)
    return SubscriptionRead.model_validate(subscription, from_attributes=True)

async def delete_subscription(session: AsyncSession, subscription_id: UUID) -> bool:
    """Delete a subscription."""
    subscription = await session.get(SubscriptionTable, subscription_id)
    if subscription is None:
        return False
    
    await session.delete(subscription)
    await session.commit()
    return True
