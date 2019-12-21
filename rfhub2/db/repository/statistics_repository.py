from typing import List

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from rfhub2.db.base import Statistics
from rfhub2.db.repository.base_repository import BaseRepository


class StatisticsRepository(BaseRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(Statistics).options(selectinload(Statistics.keywords))

    def _id_filter(self, item_id: int) -> BinaryExpression:
        return Statistics.id == item_id

    def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Statistics]:
        return (
            self.session.query((func.sum(Statistics.times_used)).label('times_used'), (func.avg(Statistics.total_elapsed_time)).label('total_elapsed_time'), Statistics.collection, Statistics.keyword)
            .group_by(Statistics.collection, Statistics.keyword)
            .order_by(Statistics.collection, Statistics.keyword)
            .offset(skip)
            .limit(limit)
            .all()
        )
