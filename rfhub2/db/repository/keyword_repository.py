from typing import List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from rfhub2.db.base import Collection, Keyword, Statistics
from rfhub2.db.repository.base_repository import BaseRepository
from rfhub2.db.repository.query_utils import glob_to_sql


class KeywordRepository(BaseRepository):
    @property
    def _items(self) -> Query:
        return self.session.query(Keyword).options(selectinload(Keyword.collection))

    def _id_filter(self, item_id: int) -> BinaryExpression:
        return Keyword.id == item_id

    def get_all(
        self,
        *,
        pattern: Optional[str] = None,
        collection_name: Optional[str] = None,
        use_doc: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Keyword]:
        filter_criteria = []
        if pattern:
            filter_criteria.append(Keyword.name.ilike(glob_to_sql(pattern)))
            if use_doc:
                filter_criteria = [
                    or_(filter_criteria[0], Keyword.doc.ilike(glob_to_sql(pattern)))
                ]
        if collection_name:
            filter_criteria.append(Collection.name.ilike(glob_to_sql(collection_name)))
        keyword_statistics = self.session.query(func.sum(Statistics.times_used).label('times_used'),
                                                (func.sum(Statistics.total_elapsed_time) / func.sum(
                                                    Statistics.times_used)).label('avg_elapsed_time'), Statistics.collection,
                                                Statistics.keyword).group_by(Statistics.collection,
                                                                             Statistics.keyword).subquery()
        return (
            self.session.query(Keyword, Collection.name, Collection.id, keyword_statistics.c.times_used.label('times_used'), keyword_statistics.c.avg_elapsed_time.label('avg_elapsed_time'))
            .join(Keyword.collection)
            # .join(Collection)
            .outerjoin(keyword_statistics, and_(Collection.name == keyword_statistics.c.collection,
                                                Keyword.name == keyword_statistics.c.keyword))
            .filter(*filter_criteria)
            .order_by(Keyword.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
