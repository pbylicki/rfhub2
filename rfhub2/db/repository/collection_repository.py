from typing import List, Optional, Tuple, Dict

from sqlalchemy import func, Column
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import BinaryExpression


from rfhub2.db.base import Collection, Keyword, KeywordStatistics
from rfhub2.model import CollectionWithStats, Collection as ModelCollection
from rfhub2.db.repository.base_repository import IdEntityRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.query_utils import glob_to_sql


class CollectionRepository(IdEntityRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.keyword_count = (
            self.session.query(
                (func.count(Keyword.id)).label("keyword_count"), Keyword.collection_id
            )
            .group_by(Keyword.collection_id)
            .subquery()
        )
        self.collection_statistics = (
            self.session.query(
                (func.sum(KeywordStatistics.times_used)).label("times_used"),
                KeywordStatistics.collection,
            )
            .group_by(KeywordStatistics.collection)
            .subquery()
        )

    @property
    def custom_column_mapping(self) -> Dict[str, Column]:
        return {
            "keyword_count": self.keyword_count_column,
            "times_used": self.times_used_column,
        }

    @property
    def keyword_count_column(self) -> Column:
        return func.coalesce(self.keyword_count.c.keyword_count, 0)

    @property
    def times_used_column(self) -> Column:
        return func.coalesce(self.collection_statistics.c.times_used, 0)

    @property
    def _items(self) -> Query:
        return (
            self.session.query(
                Collection, func.coalesce(self.keyword_count.c.keyword_count, 0)
            )
            .outerjoin(
                self.keyword_count, Collection.id == self.keyword_count.c.collection_id
            )
            .options(selectinload(Collection.keywords))
        )

    @property
    def _items_with_stats(self) -> Query:
        return (
            self.session.query(
                Collection,
                func.coalesce(self.keyword_count.c.keyword_count, 0),
                self.collection_statistics.c.times_used,
            )
            .outerjoin(
                self.collection_statistics,
                Collection.name == self.collection_statistics.c.collection,
            )
            .outerjoin(
                self.keyword_count, Collection.id == self.keyword_count.c.collection_id
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
    def from_row(row: Tuple[Collection, int]) -> ModelCollection:
        collection = row[0]
        keywords = [kw.to_nested_model() for kw in collection.keywords]
        return ModelCollection(
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
            keyword_count=row[1],
        )

    @staticmethod
    def from_stats_row(row: Tuple[Collection, int]) -> CollectionWithStats:
        return CollectionWithStats(
            **{**CollectionRepository.from_row(row).dict(), "times_used": row[2]}
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
            self.from_row(row)
            for row in (
                self._items.filter(*self.filter_criteria(pattern, libtype))
                .order_by(
                    *Collection.ordering_criteria(ordering, self.custom_column_mapping)
                )
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
                .order_by(
                    *Collection.ordering_criteria(ordering, self.custom_column_mapping)
                )
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def get_with_stats(self, item_id: int) -> Optional[CollectionWithStats]:
        result = self._items_with_stats.filter(self._id_filter(item_id)).first()
        if result:
            return self.from_stats_row(result)

    def get(self, item_id: int) -> Optional[ModelCollection]:
        result = self._items.filter(self._id_filter(item_id)).first()
        if result:
            return self.from_row(result)

    def delete(self, item_id: int) -> int:
        deleted = (
            self.session.query(Collection)
            .filter(Collection.id == item_id)
            .delete(synchronize_session=False)
        )
        self.session.commit()
        return deleted
