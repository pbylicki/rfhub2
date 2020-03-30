from sqlalchemy import Column, DateTime, Integer, PrimaryKeyConstraint, Text
from typing import List

from rfhub2.db.model.base_class import Base
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2 import model


class KeywordStatistics(Base):
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
            f"KeywordStatistics({self.collection},{self.keyword},{self.execution_time},"
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

    @staticmethod
    def create(data: model.KeywordStatistics) -> "KeywordStatistics":
        return KeywordStatistics(
            collection=data.collection,
            keyword=data.keyword,
            execution_time=data.execution_time,
            times_used=data.times_used,
            total_elapsed=data.total_elapsed,
            min_elapsed=data.min_elapsed,
            max_elapsed=data.max_elapsed,
        )

    def to_model(self) -> model.KeywordStatistics:
        return model.KeywordStatistics(
            collection=self.collection,
            keyword=self.keyword,
            execution_time=self.execution_time,
            times_used=self.times_used,
            total_elapsed=self.total_elapsed,
            min_elapsed=self.min_elapsed,
            max_elapsed=self.max_elapsed,
        )
