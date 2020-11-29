from sqlalchemy import Boolean, Column, Index, Integer, Sequence, Text
from typing import List

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.mixins import DocMixin
from rfhub2.db.repository.ordering import OrderingItem


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
