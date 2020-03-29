import unittest

from rfhub2.db.base import Collection, Keyword
from rfhub2.db.init_db import init_db
from rfhub2.db.repository.collection_repository import CollectionRepository
from rfhub2.db.repository.keyword_repository import KeywordRepository
from rfhub2.db.session import db_session


class BaseRepositoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        init_db(db_session)

    def setUp(self) -> None:
        db_session.rollback()
        db_session.query(Keyword).delete()
        db_session.query(Collection).delete()
        self.collection_repo = CollectionRepository(db_session)
        self.keyword_repo = KeywordRepository(db_session)
        self.keywords = [
            Keyword(
                name="Test setup",
                doc="Prepare test environment, use teardown after this one",
                tags="tag_1",
            ),
            Keyword(name="Login keyword", doc="Perform some check", tags="tag_2"),
            Keyword(name="Teardown", doc="Clean up environment", tags="tag_2"),
        ]
        self.app_keyword = Keyword(name="Login to Application")

        self.collections = [
            Collection(name="First collection", type="robot", keywords=self.keywords),
            Collection(
                name="Second collection", type="Robot", keywords=[self.app_keyword]
            ),
            Collection(name="Third", type="Library"),
        ]
        self.sorted_keywords = sorted(
            self.keywords + [self.app_keyword], key=lambda k: k.name
        )
        db_session.add_all(self.collections)
        db_session.commit()
        for item in self.collections:
            db_session.refresh(item)

    def tearDown(self):
        db_session.expunge_all()
