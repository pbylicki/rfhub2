import os

APP_TITLE = os.getenv("RFHUB_APP_TITLE", "rfhub2")
APP_INTERFACE = os.getenv("RFHUB_APP_INTERFACE", "0.0.0.0")
APP_PORT = int(os.getenv("PORT", 8000))
APP_LOG_LEVEL = os.getenv("RFHUB_APP_LOG_LEVEL", "info")
BASIC_AUTH_USER = os.getenv("RFHUB_BASIC_AUTH_USER", "rfhub")
BASIC_AUTH_PASSWORD = os.getenv("RFHUB_BASIC_AUTH_PASSWORD", "rfhub")
SQLALCHEMY_DB_URI = os.getenv("RFHUB_DB_URI", "sqlite:///test.db")
