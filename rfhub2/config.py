import os

APP_TITLE = os.getenv("RFHUB_APP_TITLE", "rfhub-new")
APP_INTERFACE = os.getenv("RFHUB_APP_INTERFACE", "0.0.0.0")
APP_PORT = int(os.getenv("RFHUB_APP_PORT", 8000))
APP_LOG_LEVEL = os.getenv("RFHUB_APP_LOG_LEVEL", "info")
SQLALCHEMY_DB_URI = os.getenv("RFHUB_DB_URI", "sqlite:///test.db")
