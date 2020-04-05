from typing import List, Optional, Tuple

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from rfhub2.db.base import Collection, Keyword, KeywordStatistics
from rfhub2.model import KeywordWithStats, Keyword as ModelKeyword
from rfhub2.db.repository.base_repository import IdEntityRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.query_utils import glob_to_sql


class KeywordRepository(IdEntityRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(Keyword).options(selectinload(Keyword.collection))

    @property
    def _items_with_stats(self) -> Query:
        keyword_statistics = (
            self.session.query(
                func.sum(KeywordStatistics.times_used).label("times_used"),
                (
                    func.sum(KeywordStatistics.total_elapsed)
                    / func.sum(KeywordStatistics.times_used)
                ).label("avg_elapsed"),
                KeywordStatistics.collection,
                KeywordStatistics.keyword,
            )
            .group_by(KeywordStatistics.collection, KeywordStatistics.keyword)
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
        pattern: Optional[str],
        collection_name: Optional[str],
        collection_id: Optional[int],
        use_doc: bool,
        use_tags: bool,
    ):
        filter_criteria = []
        if pattern:
            if use_tags:
                filter_criteria.append(Keyword.tags.ilike(glob_to_sql(pattern)))
            else:
                filter_criteria.append(Keyword.name.ilike(glob_to_sql(pattern)))
            if use_doc:
                filter_criteria = [
                    or_(filter_criteria[0], Keyword.doc.ilike(glob_to_sql(pattern)))
                ]
        if collection_name:
            filter_criteria.append(Collection.name.ilike(glob_to_sql(collection_name)))
        if collection_id:
            filter_criteria.append(Keyword.collection_id == collection_id)
        return filter_criteria

    @staticmethod
    def from_stats_row(row: Tuple[Keyword, int, float]) -> KeywordWithStats:
        keyword = row[0]
        return KeywordWithStats(
            id=keyword.id,
            name=keyword.name,
            doc=keyword.doc,
            args=keyword.args,
            tags=Keyword.from_json_list(keyword.tags),
            arg_string=keyword.arg_string,
            html_doc=keyword.html_doc,
            synopsis=keyword.synopsis,
            collection=keyword.collection.to_nested_model(),
            times_used=row[1],
            avg_elapsed=row[2],
        )

    def get_all(
        self,
        *,
        pattern: Optional[str] = None,
        collection_name: Optional[str] = None,
        collection_id: Optional[int] = None,
        use_doc: bool = True,
        use_tags: bool = False,
        skip: int = 0,
        limit: int = 100,
        ordering: List[OrderingItem] = None,
    ) -> List[ModelKeyword]:
        return [
            keyword.to_model()
            for keyword in (
                self.session.query(Keyword)
                .join(Keyword.collection)
                .filter(
                    *self.filter_criteria(
                        pattern, collection_name, collection_id, use_doc, use_tags
                    )
                )
                .order_by(*Keyword.ordering_criteria(ordering))
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def get_all_with_stats(
        self,
        *,
        pattern: Optional[str] = None,
        collection_name: Optional[str] = None,
        collection_id: Optional[int] = None,
        use_doc: bool = True,
        use_tags: bool = False,
        skip: int = 0,
        limit: int = 100,
        ordering: List[OrderingItem] = None,
    ) -> List[KeywordWithStats]:
        return [
            self.from_stats_row(row)
            for row in (
                self._items_with_stats.filter(
                    *self.filter_criteria(
                        pattern, collection_name, collection_id, use_doc, use_tags
                    )
                )
                .order_by(*Keyword.ordering_criteria(ordering))
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def get_with_stats(self, item_id: int) -> Optional[KeywordWithStats]:
        result = self._items_with_stats.filter(self._id_filter(item_id)).first()
        if result:
            return self.from_stats_row(result)

    def update(self, item: Keyword, update_data: dict) -> Keyword:
        if "tags" in update_data:
            update_data["tags"] = Keyword.from_json_list(update_data["tags"])
        return super().update(item, update_data)
