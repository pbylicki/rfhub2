from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic import command
from pathlib import Path
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.engine.reflection import Inspector


def has_tables(connection: Connection) -> bool:
    inspector = Inspector(connection)
    tables = inspector.get_table_names()
    return len(tables) > 0


def has_revision(connection: Connection) -> bool:
    context = MigrationContext.configure(connection)
    current_rev = context.get_current_revision()
    return current_rev is not None


def migrate_db(engine: Engine) -> None:
    config_path = Path(__file__).resolve().parent.parent / "alembic.ini"
    alembic_cfg = Config(config_path)
    with engine.begin() as connection:
        # check if database has not been migrated yet with alembic
        if has_tables(connection) and not has_revision(connection):
            # stamp database with the initial revision id, representing pre-alembic database schema
            command.stamp(alembic_cfg, "c54a916ec6c8")
        command.upgrade(alembic_cfg, "head")
