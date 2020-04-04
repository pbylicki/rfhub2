from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from rfhub2.db.base import Collection, KeywordStatistics
from rfhub2.model import CollectionWithStats, Collection as ModelCollection
from rfhub2.db.repository.base_repository import IdEntityRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.query_utils import glob_to_sql


class CollectionRepository(IdEntityRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(Collection).options(selectinload(Collection.keywords))

    @property
    def _items_with_stats(self) -> Query:
        collection_statistics = (
            self.session.query(
                (func.sum(KeywordStatistics.times_used)).label("times_used"),
                KeywordStatistics.collection,
            )
            .group_by(KeywordStatistics.collection)
            .subquery()
        )
        return (
            self.session.query(Collection, collection_statistics.c.times_used)
            .outerjoin(
                collection_statistics,
                Collection.name == collection_statistics.c.collection,
            )
            .options(selectinload(Collection.keywords))
        )

    def _id_filter(self, item_id: int) -> BinaryExpression:
        return Collection.id == item_id

    @staticmethod
    def filter_criteria(pattern: Optional[str], libtype: Optional[str]):
        filter_criteria = []
        if pattern:
            filter_criteria.append(Collection.name.ilike(glob_to_sql(pattern)))
        if libtype:
            filter_criteria.append(Collection.type.ilike(glob_to_sql(libtype)))
        return filter_criteria

    @staticmethod
    def from_stats_row(row: Tuple[Collection, int]) -> CollectionWithStats:
        collection = row[0]
        keywords = [kw.to_nested_model() for kw in collection.keywords]
        return CollectionWithStats(
            id=collection.id,
            name=collection.name,
            type=collection.type,
            version=collection.version,
            scope=collection.scope,
            named_args=collection.named_args,
            path=collection.path,
            doc=collection.doc,
            doc_format=collection.doc_format,
            html_doc=collection.html_doc,
            synopsis=collection.synopsis,
            keywords=keywords,
            times_used=row[1],
        )

    def get_all(
        self,
        *,
        pattern: Optional[str] = None,
        libtype: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        ordering: List[OrderingItem] = None,
    ) -> List[ModelCollection]:
        return [
            collection.to_model()
            for collection in (
                self._items.filter(*self.filter_criteria(pattern, libtype))
                .order_by(*Collection.ordering_criteria(ordering))
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def get_all_with_stats(
        self,
        *,
        pattern: Optional[str] = None,
        libtype: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        ordering: List[OrderingItem] = None,
    ) -> List[CollectionWithStats]:
        return [
            self.from_stats_row(row)
            for row in (
                self._items_with_stats.filter(*self.filter_criteria(pattern, libtype))
                .order_by(*Collection.ordering_criteria(ordering))
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def get_with_stats(self, item_id: int) -> Optional[CollectionWithStats]:
        result = self._items_with_stats.filter(self._id_filter(item_id)).first()
        if result:
            return self.from_stats_row(result)
