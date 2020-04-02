from rfhub2.app import create_app
from rfhub2.db.migrate import migrate_db
from rfhub2.db.session import engine

migrate_db(engine)
app = create_app()
