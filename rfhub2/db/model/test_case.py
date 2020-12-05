from sqlalchemy import Column, ForeignKey, Index, Integer, Sequence, Text
from typing import List

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.mixins import DocMixin
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.model import TestCaseCreate


class TestCase(Base, DocMixin):
    id = Column(Integer, Sequence("test_case_id_seq"), primary_key=True)
    suite_id = Column(
        Integer, ForeignKey("suite.id", ondelete="CASCADE"), nullable=False
    )
    line = Column(Integer)
    name = Column(Text, index=True)
    doc = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    template = Column(Text, nullable=True)
    timeout = Column(Text, nullable=True)
    tags = Column(Text)
    keywords = Column(Text)

    __table_args__ = (Index("ix_testcase_suite_id_name", suite_id, name, unique=True),)

    def __str__(self):  # pragma: no cover
        return (
            f"TestCase({self.id},{self.suite_id},{self.name},{self.line},{self.doc},"
            + f"{self.source},{self.template},{self.timeout},{self.tags},{self.keywords})"
        )

    def __repr__(self):  # pragma: no cover
        return str(self)

    @classmethod
    def default_ordering(cls) -> List[OrderingItem]:
        return [OrderingItem("name")]

    @staticmethod
    def create(tc: TestCaseCreate) -> "TestCase":
        return TestCase(
            suite_id=tc.suite_id,
            line=tc.line,
            name=tc.name,
            doc=tc.doc,
            source=tc.source,
            template=tc.template,
            timeout=tc.timeout,
            keywords=tc.keywords.json(),
            tags=tc.tags.json(),
        )
