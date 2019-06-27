from rfhub2.app import create_app
from rfhub2.db.init_db import init_db
from rfhub2.db.sample_data import recreate_data
from rfhub2.db.session import db_session

init_db(db_session)
recreate_data(db_session)
app = create_app()
