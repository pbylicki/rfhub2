from typing import List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from rfhub2.db.base import Collection
from rfhub2.db.base import Statistics
from rfhub2.db.repository.base_repository import BaseRepository
from rfhub2.db.repository.query_utils import glob_to_sql


class CollectionRepository(BaseRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(Collection).options(selectinload(Collection.keywords))

    def _id_filter(self, item_id: int) -> BinaryExpression:
        return Collection.id == item_id

    def get_all(
        self,
        *,
        pattern: Optional[str] = None,
        libtype: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Collection]:
        filter_criteria = []
        if pattern:
            filter_criteria.append(Collection.name.ilike(glob_to_sql(pattern)))
        if libtype:
            filter_criteria.append(Collection.type.ilike(glob_to_sql(libtype)))
        collection_statistics = self.session.query((func.sum(Statistics.times_used)).label('times_used'),
                                                   Statistics.collection).group_by(Statistics.collection).subquery()
        keyword_statistics = self.session.query(func.sum(Statistics.times_used),
                                                func.sum(Statistics.total_elapsed_time) / func.sum(
                                                    Statistics.times_used), Statistics.collection,
                                                Statistics.keyword).group_by(Statistics.collection,
                                                                             Statistics.keyword).subquery()

        q = str(self.session.query(Collection).outerjoin(collection_statistics,
                                                     Collection.name == collection_statistics.c.collection).options(
            selectinload(Collection.keywords)).filter(*filter_criteria))
        # .outerjoin(keyword_statistics, and_(Collection.name == keyword_statistics.c.collection, Collection.keywords.name == keyword_statistics.c.keyword))
        # .order_by(Collection.name)
        # .offset(skip)
        # .limit(limit).all()

        a = str(q)
        return (
            # self._items
            self.session.query(Collection, Collection.name, Collection.id, Collection.keywords, collection_statistics.c.times_used)
                # .join(Collection.keywords)
                .outerjoin(collection_statistics, Collection.name == collection_statistics.c.collection)
                .options(selectinload(Collection.keywords))
                .filter(*filter_criteria)
                .order_by(Collection.name)
                .offset(skip)
                .limit(limit)
                .all()
        )
