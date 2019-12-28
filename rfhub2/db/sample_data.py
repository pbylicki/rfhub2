from datetime import datetime, timezone
from sqlalchemy.orm.session import Session

from rfhub2.db.base import Collection, Keyword, Statistics


def recreate_data(session: Session) -> None:
    session.query(Keyword).delete()
    session.query(Collection).delete()
    session.query(Statistics).delete()
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
    statistics = [
        Statistics(
            collection="First collection",
            keyword="Test setup",
            execution_time=datetime(2019, 12, 21, 2, 30, 0, tzinfo=timezone.utc),
            times_used=10,
            total_elapsed=1000,
            min_elapsed=10,
            max_elapsed=100,
        ),
        Statistics(
            collection="First collection",
            keyword="Some keyword",
            execution_time=datetime(2019, 12, 21, 2, 30, 0, tzinfo=timezone.utc),
            times_used=5,
            total_elapsed=3000,
            min_elapsed=300,
            max_elapsed=1500,
        ),
        Statistics(
            collection="First collection",
            keyword="Some keyword",
            execution_time=datetime(2019, 12, 20, 1, 30, 0, tzinfo=timezone.utc),
            times_used=5,
            total_elapsed=2000,
            min_elapsed=200,
            max_elapsed=1000,
        ),
        Statistics(
            collection="Second collection",
            keyword="Old keyword",
            execution_time=datetime(2019, 12, 21, 1, 30, 0, tzinfo=timezone.utc),
            times_used=5,
            total_elapsed=2500,
            min_elapsed=200,
            max_elapsed=1000,
        ),
        Statistics(
            collection="Second collection",
            keyword="Old keyword",
            execution_time=datetime(2019, 12, 21, 2, 30, 0, tzinfo=timezone.utc),
            times_used=5,
            total_elapsed=2500,
            min_elapsed=100,
            max_elapsed=1000,
        ),
        Statistics(
            collection="Second collection",
            keyword="Old keyword",
            execution_time=datetime(2019, 12, 21, 3, 30, 0, tzinfo=timezone.utc),
            times_used=5,
            total_elapsed=2500,
            min_elapsed=200,
            max_elapsed=1100,
        ),
    ]
    session.add_all(collections)
    session.add_all(statistics)
    session.commit()
