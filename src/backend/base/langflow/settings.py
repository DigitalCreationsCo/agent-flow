DEV = False
STRIPE_SECRET_KEY_LIVE: str | None = None
STRIPE_SECRET_KEY_TEST: str | None = None
STRIPE_PUBLISHABLE_KEY_LIVE: str | None = None
STRIPE_PUBLISHABLE_KEY: str | None = None
LANGFLOW_HOST: str | None = None
STRIPE_WEBHOOK_SECRET: str | None = None


def _set_dev(value) -> None:
    global DEV  # noqa: PLW0603
    DEV = value


def set_dev(value) -> None:
    _set_dev(value)
