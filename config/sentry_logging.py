import sentry_sdk

sentry_sdk.init(
    dsn="https://8db2965226711e2854464196ee7cbc76@o4509168951885824.ingest.de.sentry.io/4509169144561744",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)
