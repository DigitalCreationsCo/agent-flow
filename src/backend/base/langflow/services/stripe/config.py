from dataclasses import dataclass
from typing import Optional
import os
import stripe

@dataclass
class StripeConfig:
    client: stripe.StripeClient
    webhook_secret: Optional[str]

def get_stripe_config() -> StripeConfig:
    """Get Stripe configuration."""

    stripe.api_key = (
        os.getenv("STRIPE_SECRET_KEY_LIVE") or 
        os.getenv("STRIPE_SECRET_KEY_TEST")
    )
    
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")          
    
    return StripeConfig(
        client=stripe,
        webhook_secret=webhook_secret
    )