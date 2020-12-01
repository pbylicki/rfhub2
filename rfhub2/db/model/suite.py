from sqlalchemy import Boolean, Column, Index, Integer, Sequence, Text
from typing import List

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.mixins import DocMixin
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.model import KeywordRefList, SuiteHierarchy, SuiteHierarchyWithId


class Suite(Base, DocMixin):
    id = Column(Integer, Sequence("suite_id_seq"), primary_key=True)
    name = Column(Text, index=True)
    longname = Column(Text)
    doc = Column(Text)
    keywords = Column(Text)
    is_root = Column(Boolean)

    __table_args__ = (Index("ix_suite_longname", longname, unique=True),)

    def __str__(self):  # pragma: no cover
        return f"Suite({self.id},{self.name},{self.longname},{self.doc},{self.keywords},{self.is_root})"

    def __repr__(self):  # pragma: no cover
        return str(self)

    @classmethod
    def default_ordering(cls) -> List[OrderingItem]:
        return [OrderingItem("longname")]

    @staticmethod
    def create(hierarchy: SuiteHierarchy, is_root: bool = True) -> "Suite":
        return Suite(
            name=hierarchy.name,
            longname=hierarchy.longname,
            doc=hierarchy.doc,
            keywords=hierarchy.keywords.json(),
            is_root=is_root,
        )

    def to_hierarchy(self) -> SuiteHierarchyWithId:
        return SuiteHierarchyWithId(
            id=self.id,
            name=self.name,
            longname=self.longname,
            doc=self.doc,
            is_root=self.is_root,
            keywords=KeywordRefList.parse_raw(self.keywords),
            suites=[],
        )
