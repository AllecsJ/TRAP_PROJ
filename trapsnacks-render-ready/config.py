import os


# config.py
# Settings for the whole application. Change values here, not inside other files.


class Config:
    # Used to sign login cookies and protect forms. Change it to any long random text.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'local-development-only-change-me')

    # The database is one file called trapsnacks.db, created in the "instance" folder.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///trapsnacks.db')

    # FR 4 SR-4: minutes a rider has to pick up an order after accepting it.
    PICKUP_MINUTES = 12

    # FR 4 SR-5: minutes before staff are alerted that no rider has accepted an offer.
    NO_RIDER_ALERT_MINUTES = 2


import os

database_url =  os.environ.get(
    "DATABASE_URL",
    "postgres://", "postgresql://", 1
)
