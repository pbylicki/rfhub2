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


@dataclass
class StatisticsFilterParams:
    collection: str
    keyword: Optional[str] = None
    execution_time: Optional[datetime] = None
    execution_time_from: Optional[datetime] = None
    execution_time_to: Optional[datetime] = None


class StatisticsRepository(BaseRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(Statistics)

    @staticmethod
    def filter_criteria(params: StatisticsFilterParams):
        filter_criteria = []
        if params.collection:
            filter_criteria.append(Statistics.collection == params.collection)
        if params.keyword:
            filter_criteria.append(Statistics.keyword == params.keyword)
        if params.execution_time:
            filter_criteria.append(Statistics.execution_time == params.execution_time)
        else:
            if params.execution_time_from:
                filter_criteria.append(
                    Statistics.execution_time >= params.execution_time_from
                )
            if params.execution_time_to:
                filter_criteria.append(
                    Statistics.execution_time <= params.execution_time_to
                )
        return filter_criteria

    def get_aggregated(
        self, filter_params: StatisticsFilterParams
    ) -> AggregatedStatistics:
        result = (
            self.session.query(
                func.coalesce(func.sum(Statistics.times_used), 0).label("times_used"),
                func.coalesce(func.sum(Statistics.total_elapsed), 0).label(
                    "total_elapsed"
                ),
                func.coalesce(
                    func.sum(Statistics.total_elapsed)
                    / func.sum(Statistics.times_used),
                    0,
                ).label("avg_elapsed"),
                func.coalesce(func.min(Statistics.min_elapsed), 0).label("min_elapsed"),
                func.coalesce(func.max(Statistics.max_elapsed), 0).label("max_elapsed"),
            )
            .filter(*self.filter_criteria(filter_params))
            .first()
        )
        return AggregatedStatistics(*result)

    def get_many(
        self, *, filter_params: StatisticsFilterParams, skip: int = 0, limit: int = 100
    ) -> List[Statistics]:
        return (
            self._items.filter(*self.filter_criteria(filter_params))
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
        self, filter_params: Optional[StatisticsFilterParams] = None
    ) -> int:
        filter_criteria = self.filter_criteria(filter_params) if filter_params else []
        row_count = self._items.filter(*filter_criteria).delete()
        self.session.commit()
        return row_count
