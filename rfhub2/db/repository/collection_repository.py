from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session

from rfhub2.db.base import Collection
from rfhub2.db.repository.query_utils import glob_to_sql


class CollectionRepository:

    def __init__(self, db_session: Session):
        self.session = db_session

    @property
    def _collections(self) -> Query:
        return self.session.query(Collection).options(selectinload(Collection.keywords))

    def add(self, collection: Collection) -> Collection:
        self.session.add(collection)
        self.session.commit()
        self.session.refresh(collection)
        return collection

    def delete(self, collection_id: int) -> int:
        row_count = self._collections.filter(Collection.id == collection_id).delete()
        self.session.commit()
        return row_count

    def get(self, collection_id: int) -> Optional[Collection]:
        return self._collections.get(collection_id)

    def get_all(self, *, pattern: Optional[str] = None,
                libtype: Optional[str] = None,
                skip: int = 0,
                limit: int = 100) -> List[Collection]:
        filter_criteria = []
        if pattern:
            filter_criteria.append(Collection.name.ilike(glob_to_sql(pattern)))
        if libtype:
            filter_criteria.append(Collection.type.ilike(glob_to_sql(libtype)))
        return self._collections.filter(*filter_criteria).offset(skip).limit(limit).all()
