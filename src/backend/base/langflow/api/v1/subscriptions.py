from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from langflow.api.utils import DbSession
from langflow.schema.product import (
    PriceRead,
    ProductRead,
)
from langflow.schema.subscription import SubscriptionCreate, SubscriptionRead, SubscriptionUpdate
from langflow.services.database.models.price.crud import get_prices
from langflow.services.database.models.product.crud import get_products
from langflow.services.database.models.subscription.crud import (
    create_subscription,
    delete_subscription,
    get_subscription,
    get_subscriptions,
    update_subscription,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/subscriptions")
async def list_subscriptions(session: DbSession) -> list[SubscriptionRead]:
    try:
        return await get_subscriptions(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/subscription/{subscription_id}", response_model=SubscriptionRead)
async def get_subscription_by_id(subscription_id: UUID, session: DbSession) -> SubscriptionRead:
    try:
        subscription = await get_subscription(session, subscription_id)
        if subscription is None:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/subscriptions", response_model=SubscriptionRead)
async def create_new_subscription(subscription: SubscriptionCreate, session: DbSession) -> SubscriptionRead:
    try:
        return await create_subscription(session, subscription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/subscriptions/{subscription_id}", response_model=SubscriptionRead)
async def update_subscription_by_id(
    subscription_id: UUID,
    subscription: SubscriptionUpdate,
    session: DbSession,
) -> SubscriptionRead:
    try:
        updated_subscription = await update_subscription(session, subscription_id, subscription)
        if updated_subscription is None:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return updated_subscription
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/subscriptions/{subscription_id}", status_code=204)
async def delete_subscription_by_id(subscription_id: UUID, session: DbSession) -> None:
    try:
        deleted = await delete_subscription(session, subscription_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Subscription not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/products", response_model=list[ProductRead])
async def list_products(
    session: DbSession,
    # active: Optional[bool] = None
):
    """Get all products with their prices."""
    try:
        products = await get_products(session)
        print(f"get products: {products}")
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/prices", response_model=list[PriceRead])
async def list_prices(session: DbSession):
    """Get all prices."""
    try:
        print("Starting prices fetch...")
        prices = await get_prices(session)
        print(f"Raw prices data: {[price.model_dump() for price in prices]}")
        return prices
    except ValidationError as ve:
        print(f"Validation error: {ve}")
        raise HTTPException(status_code=500, detail=str(ve)) from ve
    except Exception as e:
        print(f"Error in list_prices: {e!s}")
        print(f"Error type: {type(e)}")
        import traceback

        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e)) from e
