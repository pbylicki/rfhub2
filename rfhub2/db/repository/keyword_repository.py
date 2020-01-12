from typing import List, Optional, Tuple

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from rfhub2.db.base import Collection, Keyword, Statistics
from rfhub2.model import KeywordWithStats
from rfhub2.db.repository.base_repository import IdEntityRepository
from rfhub2.db.repository.query_utils import glob_to_sql


class KeywordRepository(IdEntityRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(Keyword).options(selectinload(Keyword.collection))

    @property
    def _items_with_stats(self) -> Query:
        keyword_statistics = (
            self.session.query(
                func.sum(Statistics.times_used).label("times_used"),
                (
                    func.sum(Statistics.total_elapsed) / func.sum(Statistics.times_used)
                ).label("avg_elapsed"),
                Statistics.collection,
                Statistics.keyword,
            )
            .group_by(Statistics.collection, Statistics.keyword)
            .subquery()
        )
        return (
            self.session.query(
                Keyword,
                keyword_statistics.c.times_used,
                keyword_statistics.c.avg_elapsed,
            )
            .options(selectinload(Keyword.collection))
            .join(Keyword.collection)
            .outerjoin(
                keyword_statistics,
                and_(
                    Collection.name == keyword_statistics.c.collection,
                    Keyword.name == keyword_statistics.c.keyword,
                ),
            )
        )

    def _id_filter(self, item_id: int) -> BinaryExpression:
        return Keyword.id == item_id

    @staticmethod
    def filter_criteria(
        pattern: Optional[str], collection_name: Optional[str], use_doc: bool
    ):
        filter_criteria = []
        if pattern:
            filter_criteria.append(Keyword.name.ilike(glob_to_sql(pattern)))
            if use_doc:
                filter_criteria = [
                    or_(filter_criteria[0], Keyword.doc.ilike(glob_to_sql(pattern)))
                ]
        if collection_name:
            filter_criteria.append(Collection.name.ilike(glob_to_sql(collection_name)))
        return filter_criteria

    @staticmethod
    def from_stats_row(row: Tuple[Keyword, int, float]) -> KeywordWithStats:
        return KeywordWithStats(
            **row[0].__dict__, **{"times_used": row[1], "avg_elapsed": row[2]}
        )

    def get_all(
        self,
        *,
        pattern: Optional[str] = None,
        collection_name: Optional[str] = None,
        use_doc: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Keyword]:
        return (
            self.session.query(Keyword)
            .join(Keyword.collection)
            .filter(*self.filter_criteria(pattern, collection_name, use_doc))
            .order_by(Keyword.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all_with_stats(
        self,
        *,
        pattern: Optional[str] = None,
        collection_name: Optional[str] = None,
        use_doc: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[KeywordWithStats]:
        return [
            self.from_stats_row(row)
            for row in (
                self._items_with_stats.filter(
                    *self.filter_criteria(pattern, collection_name, use_doc)
                )
                .order_by(Keyword.name)
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def get_with_stats(self, item_id: int) -> Optional[KeywordWithStats]:
        result = self._items_with_stats.filter(self._id_filter(item_id)).first()
        if result:
            return self.from_stats_row(result)
