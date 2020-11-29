from sqlalchemy import Column, ForeignKey, Index, Integer, Sequence, Text

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.mixins import DocMixin


class TestCase(Base, DocMixin):
    id = Column(Integer, Sequence("test_case_id_seq"), primary_key=True)
    suite_id = Column(
        Integer, ForeignKey("suite.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(Text, index=True)
    longname = Column(Text)
    doc = Column(Text)
    tags = Column(Text)
    keywords = Column(Text)

    __table_args__ = (Index("ix_test_case_longname", longname, unique=True),)

    def __str__(self):  # pragma: no cover
        return f"TestCase({self.id},{self.suite_id},{self.name},{self.longname},{self.doc},{self.tags},{self.keywords})"

    def __repr__(self):  # pragma: no cover
        return str(self)
