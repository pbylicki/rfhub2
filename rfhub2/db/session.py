from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlite3

from rfhub2 import config


def create_sqlalchemy_engine(db_uri: str) -> Engine:
    if db_uri.startswith("sqlite://"):
        engine_kwargs = {"connect_args": {"check_same_thread": False}}
    else:
        engine_kwargs = {}
    return create_engine(
        config.SQLALCHEMY_DB_URI, pool_pre_ping=True, echo=False, **engine_kwargs
    )


@event.listens_for(Engine, "connect")
def set_sqlite_fk_pragma(db_api_connection, _):
    """
    Setting foreign keys pragma is required to enable on delete cascade behavior
    for foreign key fields which is by default disabled
    """
    if isinstance(db_api_connection, sqlite3.Connection):
        cursor = db_api_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


engine = create_sqlalchemy_engine(config.SQLALCHEMY_DB_URI)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
