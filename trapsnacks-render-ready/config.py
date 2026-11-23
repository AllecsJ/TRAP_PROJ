
import os

# Settings for the whole TrapSnacks application.

class Config:
    # Used to sign login cookies and protect forms.
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "local-development-only-change-me"
    )

    # Connect to Neon PostgreSQL through Render.
    # SQLite is used only if DATABASE_URL is not configured.
    database_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///trapsnacks.db"
    )

    # Support older PostgreSQL URL formats.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql://", 1
        )

    # Use the psycopg PostgreSQL driver.
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # Minutes a rider has to pick up an order.
    PICKUP_MINUTES = 12

    # Minutes before staff are alerted about no rider.
    NO_RIDER_ALERT_MINUTES = 2
