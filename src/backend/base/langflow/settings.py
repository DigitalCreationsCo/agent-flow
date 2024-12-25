from dataclasses import Field
from typing import Optional


DEV = False
STRIPE_SECRET_KEY_LIVE: Optional[str] = None
STRIPE_SECRET_KEY_TEST: Optional[str] = None
STRIPE_PUBLISHABLE_KEY_LIVE: Optional[str] = None
STRIPE_PUBLISHABLE_KEY: Optional[str] = None
LANGFLOW_HOST: Optional[str] = None
STRIPE_WEBHOOK_SECRET: Optional[str] = None


def _set_dev(value) -> None:
    global DEV  # noqa: PLW0603
    DEV = value


def set_dev(value) -> None:
    _set_dev(value)
