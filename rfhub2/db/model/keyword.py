from sqlalchemy import Column, ForeignKey, Integer, Sequence, Text
from typing import List

from rfhub2.db.model.base_class import Base
from rfhub2.db.model.mixins import KeywordMixin
from rfhub2.db.repository.ordering import OrderingItem


class Keyword(Base, KeywordMixin):
    id = Column(Integer, Sequence("keyword_id_seq"), primary_key=True)
    name = Column(Text, index=True)
    doc = Column(Text)
    args = Column(Text)
    tags = Column(Text)
    collection_id = Column(
        Integer, ForeignKey("collection.id", ondelete="CASCADE"), nullable=False
    )

    def __str__(self):  # pragma: no cover
        return f"Keyword({self.id},{self.name},{self.doc},{self.args},{self.tags},{self.collection_id})"

    def __repr__(self):  # pragma: no cover
        return str(self)

    @classmethod
    def default_ordering(cls) -> List[OrderingItem]:
        return [OrderingItem("name")]
