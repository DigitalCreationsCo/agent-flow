import json
import os
import select
from typing import Any
from uuid import UUID

import stripe
import stripe.error
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.schema.product import PriceCreate, ProductCreate
from langflow.services.auth.utils import get_current_active_user
from langflow.services.database.models.price.crud import create_price, delete_price
from langflow.services.database.models.product.crud import create_product, delete_product, update_product
from langflow.services.database.models.product.model import ProductType
from langflow.services.database.models.subscription.crud import create_subscription, update_subscription
from langflow.services.database.models.user.crud import update_user_customer_id
from langflow.services.database.models.user.model import User
from langflow.services.database.utils import session_getter
from langflow.services.deps import get_db_service
from langflow.utils.redirect import get_error_redirect

router = APIRouter(prefix="/stripe", tags=["Stripe"])


# Response models
class CheckoutResponse(BaseModel):
    sessionId: str | None = None
    sessionUrl: str | None = None
    errorRedirect: str | None = None


RELEVANT_EVENTS = {
    "product.created",
    "product.updated",
    "product.deleted",
    "price.created",
    "price.updated",
    "price.deleted",
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
}


async def handle_product_event(
    event_type: str,
    stripe_product: Any,
    session: DbSession,
) -> None:
    """Handle product events."""
    try:
        print(f"Handling product event: {event_type}")
        print(f"product id: {stripe_product.id}")
        print(f"stripe_product: {stripe_product}")
        print(f"stripe_product metadata: {stripe_product.metadata}")
        if event_type == "product.deleted":
            await delete_product(session, stripe_product.id)
        else:
            print("test")
            print(f"stripe metadata type {stripe_product.metadata.get('type') or ProductType.BASIC.value}")
            product_data = {
                "id": stripe_product.id,
                "name": stripe_product.name,
                "description": stripe_product.description,
                "is_active": stripe_product.active,
                "product_type": stripe_product.metadata.get("type") or ProductType.BASIC.value,
                "stripe_metadata": stripe_product.metadata,
            }
            print(f"product_data: {product_data}")
            if event_type == "product.created":
                print(f"event_type: {event_type}")
                product_model = ProductCreate(**product_data)
                print(f"product_model: {product_model}")
                await create_product(session, product=product_model)
            else:
                await update_product(session, stripe_product.id, **product_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to handle product event: {e!s}"
        )


async def handle_price_event(
    event_type: str,
    stripe_price: Any,
    session=DbSession,
) -> None:
    """Handle price events."""
    try:
        print(f"Handling price event: {event_type}")
        print(f"price id: {stripe_price.id}")
        print(f"price data: {stripe_price}")
        if event_type == "price.deleted":
            await delete_price(session, stripe_price.id)
        else:
            price_data = {
                "id": stripe_price.id,
                "name": stripe_price.nickname or "",
                "unit_amount": stripe_price.unit_amount,
                "currency": stripe_price.currency,
                "type": stripe_price.type,
                "interval": getattr(stripe_price, "interval", None),
                "interval_count": getattr(stripe_price, "interval_count", None),
                "trial_period_days": getattr(stripe_price, "trial_period_days", None),
                "stripe_metadata": stripe_price.metadata,
                "product_id": stripe_price.product,
            }
            price_model = PriceCreate(**price_data)
            await create_price(session, price=price_model)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to handle price event: {e!s}"
        )


async def handle_subscription_event(
    event_type: str,
    subscription: Any,
    session=DbSession,
) -> None:
    """Handle subscription events."""
    try:
        subscription_data = {
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "current_period_start": subscription.current_period_start,
            "cancel_at": getattr(subscription, "cancel_at", None),
            "canceled_at": getattr(subscription, "canceled_at", None),
            "trial_end": getattr(subscription, "trial_end", None),
            "trial_start": getattr(subscription, "trial_start", None),
            "stripe_metadata": subscription.metadata,
        }

        if event_type == "customer.subscription.created":
            await create_subscription(session, **subscription_data)
        else:
            await update_subscription(session, subscription.id, **subscription_data)

        # Update user's customer ID if needed
        await update_user_customer_id(session, subscription.customer)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to handle subscription event: {e!s}"
        )


@router.post("/")
async def test():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "success"})


@router.post("/webhook")
async def stripe_webhook(request: Request) -> Response:
    """Handle Stripe webhook events."""
    try:
        # Get raw payload
        payload = await request.body()

        try:
            # Parse the JSON payload
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        except ValueError as e:
            print(f"Invalid payload: {e!s}")
            return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Invalid payload")

        # get dbsession here
        async with session_getter(get_db_service()) as session:
            Response(status_code=status.HTTP_200_OK)  # Respond to stripe immediately
            # Handle the event
            if event.type.startswith("product"):
                await handle_product_event(event.type, event.data.object, session)
            elif event.type.startswith("price"):
                await handle_price_event(event.type, event.data.object, session)
            elif event.type.startswith("customer.subscription"):
                await handle_subscription_event(event.type, event.data.object, session)
            elif event.type == "checkout.session.completed":
                if event.data.object.mode == "subscription":
                    subscription = stripe.Subscription.retrieve(event.data.object.subscription)
                    await handle_subscription_event("customer.subscription.created", subscription, session)
            else:
                print(f"Unhandled event type {event.type}")

            return None

    except Exception as e:
        print(f"Error processing webhook: {e!s}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(e))


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    price_id: str,
    redirect_path: str = "/settings/billing",
    current_user=get_current_active_user,
    session=Depends(DbSession),
) -> CheckoutResponse:
    """Create a Stripe checkout session."""
    try:
        # Retrieve or create the customer in Stripe
        try:
            customer = await create_or_get_stripe_customer(
                user_id=current_user.id, username=current_user.username, session=session
            )
        except Exception as err:
            raise HTTPException(status_code=400, detail="Unable to access customer record.") from err

        host = os.getenv("LANGFLOW_HOST").rstrip("/")

        print(f"Host: {host}")

        params = {
            "allow_promotion_codes": True,
            "billing_address_collection": "required",
            "customer": customer,
            "customer_update": {"address": "auto"},
            "line_items": [{"price": price_id, "quantity": 1}],
            "mode": "subscription",
            "success_url": f"{host}/settings/billing",
            "cancel_url": f"{host}/settings/billing",
        }

        # Create checkout session
        try:
            stripe_session = await stripe.checkout.Session.create(**params)
            return CheckoutResponse(
                sessionId=stripe_session.id,
                sessionUrl=stripe_session.url,  # Stripe provides the URL directly
            )
        except Exception as err:
            raise HTTPException(status_code=400, detail="Unable to create checkout session.") from err

    except Exception as error:
        return CheckoutResponse(
            errorRedirect=get_error_redirect(
                redirect_path, str(error), "Please try again later or contact a system administrator."
            )
        )


@router.post("/portal")
async def create_portal_session(
    current_path: str, current_user: CurrentActiveUser = get_current_active_user, session=Depends(DbSession)
) -> str:
    """Create a Stripe billing portal session."""
    try:
        # Retrieve or create the customer in Stripe
        try:
            customer = await create_or_get_stripe_customer(
                user_id=current_user.id, username=current_user.username, session=session
            )
        except Exception as err:
            raise HTTPException(status_code=400, detail="Unable to access customer record.") from err

        if not customer:
            raise HTTPException(status_code=400, detail="Could not get customer.")

        try:
            portal = await stripe.billing_portal.Session.create(
                customer=customer,
                return_url=os.getenv("LANGFLOW_HOST").rstrip("/"),
            )
            if not portal.url:
                raise HTTPException(status_code=400, detail="Could not create billing portal")
            return portal.url
        except Exception as err:
            raise HTTPException(status_code=400, detail="Could not create billing portal") from err

    except Exception as error:
        return get_error_redirect(current_path, str(error), "Please try again later or contact a system administrator.")


async def create_or_get_stripe_customer(user_id: UUID, username: str, session=Depends(DbSession)) -> str:
    """Create or get a Stripe customer ID for the user."""
    try:
        # First, check if user already has a stripe_customer_id
        stmt = select(User).where(User.id == user_id)
        user: User = (await session.exec(stmt)).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # If user has a stripe_customer_id, verify it exists in Stripe
        if user.stripe_customer_id:
            try:
                # Verify the customer still exists in Stripe
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
                if customer and not customer.get("deleted", False):
                    return user.stripe_customer_id
            except stripe.InvalidRequestError:
                # Customer doesn't exist in Stripe, we'll create a new one
                pass

        # Create new customer in Stripe
        customer = stripe.Customer.create(
            email=username,  # Assuming username is email, adjust if needed
            metadata={"user_id": str(user_id), "username": username},
        )

        # Update user with new stripe_customer_id
        user.stripe_customer_id = customer.id
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return customer.id

    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {e!s}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating/getting Stripe customer: {e!s}")
