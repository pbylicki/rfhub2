from pydantic import BaseConfig
from pydantic.dataclasses import dataclass
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm.query import Query
from typing import List, Optional

from rfhub2.db.base import Statistics
from rfhub2.db.repository.base_repository import BaseRepository


class Config(BaseConfig):
    orm_mode = True


@dataclass(config=Config)
class AggregatedStatistics:

    times_used: int
    total_elapsed: int
    avg_elapsed: float
    min_elapsed: int
    max_elapsed: int


class StatisticsRepository(BaseRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(Statistics)

    @staticmethod
    def filter_criteria(
        collection: Optional[str],
        keyword: Optional[str],
        execution_time: Optional[datetime],
    ):
        filter_criteria = []
        if collection:
            filter_criteria.append(Statistics.collection == collection)
        if keyword:
            filter_criteria.append(Statistics.keyword == keyword)
        if execution_time:
            filter_criteria.append(Statistics.execution_time == execution_time)
        return filter_criteria

    def get_aggregated(
        self,
        *,
        collection: str,
        keyword: Optional[str] = None,
        execution_time: Optional[datetime] = None,
    ) -> AggregatedStatistics:
        result = (
            self.session.query(
                func.coalesce(func.sum(Statistics.times_used), 0).label("times_used"),
                func.coalesce(func.sum(Statistics.total_elapsed), 0).label(
                    "total_elapsed"
                ),
                func.coalesce(func.avg(Statistics.total_elapsed), 0).label(
                    "avg_elapsed"
                ),
                func.coalesce(func.min(Statistics.min_elapsed), 0).label("min_elapsed"),
                func.coalesce(func.max(Statistics.max_elapsed), 0).label("max_elapsed"),
            )
            .filter(*self.filter_criteria(collection, keyword, execution_time))
            .first()
        )
        return AggregatedStatistics(*result)

    def get_many(
        self,
        *,
        collection: str,
        keyword: Optional[str] = None,
        execution_time: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Statistics]:
        return (
            self._items.filter(
                *self.filter_criteria(collection, keyword, execution_time)
            )
            .order_by(
                Statistics.collection,
                Statistics.keyword,
                Statistics.execution_time.desc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_many(
        self,
        *,
        collection: Optional[str] = None,
        keyword: Optional[str] = None,
        execution_time: Optional[datetime] = None,
    ) -> int:
        row_count = self._items.filter(
            *self.filter_criteria(collection, keyword, execution_time)
        ).delete()
        self.session.commit()
        return row_count
