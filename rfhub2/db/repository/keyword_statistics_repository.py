from pydantic import BaseConfig
from pydantic.dataclasses import dataclass
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm.query import Query
from typing import List, Optional

from rfhub2.db.base import KeywordStatistics
from rfhub2.db.repository.base_repository import BaseRepository
from rfhub2.db.repository.ordering import OrderingItem


class Config(BaseConfig):
    orm_mode = True


@dataclass(config=Config)
class AggregatedKeywordStatistics:

    times_used: int
    total_elapsed: int
    avg_elapsed: float
    min_elapsed: int
    max_elapsed: int


@dataclass
class KeywordStatisticsFilterParams:
    collection: str
    keyword: Optional[str] = None
    execution_time: Optional[datetime] = None
    execution_time_from: Optional[datetime] = None
    execution_time_to: Optional[datetime] = None


class KeywordStatisticsRepository(BaseRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(KeywordStatistics)

    @staticmethod
    def filter_criteria(params: KeywordStatisticsFilterParams):
        filter_criteria = []
        if params.collection:
            filter_criteria.append(KeywordStatistics.collection == params.collection)
        if params.keyword:
            filter_criteria.append(KeywordStatistics.keyword == params.keyword)
        if params.execution_time:
            filter_criteria.append(
                KeywordStatistics.execution_time == params.execution_time
            )
        else:
            if params.execution_time_from:
                filter_criteria.append(
                    KeywordStatistics.execution_time >= params.execution_time_from
                )
            if params.execution_time_to:
                filter_criteria.append(
                    KeywordStatistics.execution_time <= params.execution_time_to
                )
        return filter_criteria

    def get_aggregated(
        self, filter_params: KeywordStatisticsFilterParams
    ) -> AggregatedKeywordStatistics:
        result = (
            self.session.query(
                func.coalesce(func.sum(KeywordStatistics.times_used), 0).label(
                    "times_used"
                ),
                func.coalesce(func.sum(KeywordStatistics.total_elapsed), 0).label(
                    "total_elapsed"
                ),
                func.coalesce(
                    func.sum(KeywordStatistics.total_elapsed)
                    / func.sum(KeywordStatistics.times_used),
                    0,
                ).label("avg_elapsed"),
                func.coalesce(func.min(KeywordStatistics.min_elapsed), 0).label(
                    "min_elapsed"
                ),
                func.coalesce(func.max(KeywordStatistics.max_elapsed), 0).label(
                    "max_elapsed"
                ),
            )
            .filter(*self.filter_criteria(filter_params))
            .first()
        )
        return AggregatedKeywordStatistics(*result)

    def get_many(
        self,
        *,
        filter_params: KeywordStatisticsFilterParams,
        skip: int = 0,
        limit: int = 100,
        ordering: List[OrderingItem] = None,
    ) -> List[KeywordStatistics]:
        return [
            stat.to_model()
            for stat in (
                self._items.filter(*self.filter_criteria(filter_params))
                .order_by(*KeywordStatistics.ordering_criteria(ordering))
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def add_many(self, items: List[KeywordStatistics]) -> int:
        count: int = len(items)
        self.session.bulk_save_objects(items)
        self.session.commit()
        return count

    def delete_many(
        self, filter_params: Optional[KeywordStatisticsFilterParams] = None
    ) -> int:
        filter_criteria = self.filter_criteria(filter_params) if filter_params else []
        row_count = self._items.filter(*filter_criteria).delete()
        self.session.commit()
        return row_count
