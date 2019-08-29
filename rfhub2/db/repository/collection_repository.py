from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from rfhub2.db.base import Collection
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
        return (
            self._items.filter(*filter_criteria)
            .order_by(Collection.name)
            .offset(skip)
            .limit(limit)
            .all()
        )
