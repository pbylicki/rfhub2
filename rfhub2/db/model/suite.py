from sqlalchemy import Boolean, Column, Index, Integer, Sequence, Text
from typing import List, Optional

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.mixins import DocMixin
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.model import (
    KeywordRefList,
    NestedSuite,
    SuiteHierarchy,
    SuiteHierarchyWithId,
    SuiteMetadata,
)


class Suite(Base, DocMixin):
    id = Column(Integer, Sequence("suite_id_seq"), primary_key=True)
    name = Column(Text, index=True)
    longname = Column(Text)
    doc = Column(Text)
    keywords = Column(Text)
    metadata_items = Column(Text)
    source = Column(Text)
    is_root = Column(Boolean)
    rpa = Column(Boolean)

    __table_args__ = (Index("ix_suite_longname", longname, unique=True),)

    def __str__(self):  # pragma: no cover
        return (
            f"Suite({self.id},{self.name},{self.longname},{self.doc},{self.source},"
            + f"{self.keywords},{self.metadata_items},{self.is_root},{self.rpa})"
        )

    def __repr__(self):  # pragma: no cover
        return str(self)

    @classmethod
    def default_ordering(cls) -> List[OrderingItem]:
        return [OrderingItem("longname")]

    @staticmethod
    def create(
        hierarchy: SuiteHierarchy,
        is_root: bool = True,
        parent: Optional[SuiteHierarchyWithId] = None,
    ) -> "Suite":
        return Suite(
            name=hierarchy.name,
            longname=f"{parent.longname}.{hierarchy.name}"
            if parent
            else hierarchy.name,
            doc=hierarchy.doc,
            source=hierarchy.source,
            keywords=hierarchy.keywords.json(),
            is_root=is_root,
            metadata_items=hierarchy.metadata.json(),
            rpa=hierarchy.rpa,
        )

    def to_hierarchy(self) -> SuiteHierarchyWithId:
        return SuiteHierarchyWithId(
            id=self.id,
            name=self.name,
            longname=self.longname,
            doc=self.doc,
            source=self.source,
            is_root=self.is_root,
            keywords=KeywordRefList.parse_raw(self.keywords),
            suites=[],
            metadata=SuiteMetadata.parse_raw(self.metadata_items),
            rpa=self.rpa,
        )

    def to_nested(self) -> NestedSuite:
        return NestedSuite(id=self.id, name=self.name, longname=self.longname)
