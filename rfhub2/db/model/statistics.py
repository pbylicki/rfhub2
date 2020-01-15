from sqlalchemy import Column, DateTime, Integer, PrimaryKeyConstraint, Text
from typing import List

from rfhub2.db.model.base_class import Base
from rfhub2.db.repository.ordering import OrderingItem


class Statistics(Base):
    collection = Column(Text)
    keyword = Column(Text)
    execution_time = Column(DateTime(timezone=True))
    times_used = Column(Integer)
    total_elapsed = Column(Integer)
    min_elapsed = Column(Integer)
    max_elapsed = Column(Integer)

    __table_args__ = (PrimaryKeyConstraint(collection, keyword, execution_time),)

    def __str__(self):  # pragma: no cover
        return (
            f"Statistics({self.collection},{self.keyword},{self.execution_time},"
            + f"{self.times_used},{self.total_elapsed},{self.min_elapsed},{self.max_elapsed})"
        )

    def __repr__(self):  # pragma: no cover
        return str(self)

    @classmethod
    def default_ordering(cls) -> List[OrderingItem]:
        return [
            OrderingItem("collection"),
            OrderingItem("keyword"),
            OrderingItem("execution_time", False),
        ]
