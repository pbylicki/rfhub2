from sqlalchemy.orm.session import Session

from rfhub2.db.base import Base


def init_db(session: Session) -> None:
    Base.metadata.create_all(bind=session.bind)
