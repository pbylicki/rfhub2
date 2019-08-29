from sqlalchemy.orm.session import Session

from rfhub2.db.base import Collection, Keyword


def recreate_data(session: Session) -> None:
    session.query(Keyword).delete()
    session.query(Collection).delete()
    keywords = [
        Keyword(
            name="Test setup",
            doc="Prepare test environment, use teardown after this one",
        ),
        Keyword(name="Some keyword", doc="Perform some check"),
        Keyword(name="Teardown", doc="Clean up environment"),
    ]
    collections = [
        Collection(name="First collection", type="robot", keywords=keywords),
        Collection(name="Second collection", type="Robot"),
        Collection(name="Third", type="Library"),
    ]
    session.add_all(collections)
    session.commit()
