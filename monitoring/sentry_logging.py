import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import os
from dotenv import load_dotenv

load_dotenv()

sentry_logging = LoggingIntegration(
    level=None,  # Capture warnings and errors
    event_level=None  # Don't send logs as events unless desired
)

SENTRY_DSN = os.getenv("SENTRY_DSN")


def init_sentry():
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[sentry_logging],
            traces_sample_rate=0.0,  # Deactivated for CLI
            send_default_pii=True
        )


def log_sentry(message: str, user: dict | None = None, level: str = "info"):
    if user and "email" in user:
        sentry_sdk.set_user({"email": user["email"]})
    sentry_sdk.capture_message(message, level=level)
