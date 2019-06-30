from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session

from rfhub2.db.base import Collection, Keyword
from rfhub2.db.repository.query_utils import glob_to_sql


class KeywordRepository:

    def __init__(self, db_session: Session):
        self.session = db_session

    @property
    def _keywords(self) -> Query:
        return self.session.query(Keyword).options(selectinload(Keyword.collection))

    def add(self, keyword: Keyword) -> Keyword:
        self.session.add(keyword)
        self.session.commit()
        self.session.refresh(keyword)
        return keyword

    def get(self, keyword_id: int) -> Optional[Keyword]:
        return self._keywords.get(keyword_id)

    def get_all(self, *, pattern: Optional[str] = None,
                collection_name: Optional[str] = None,
                use_doc: bool = True,
                skip: int = 0,
                limit: int = 100) -> List[Keyword]:
        filter_criteria = []
        if pattern:
            filter_criteria.append(Keyword.name.ilike(glob_to_sql(pattern)),)
            if use_doc:
                filter_criteria = [or_(filter_criteria[0], Keyword.doc.ilike(glob_to_sql(pattern)))]
        if collection_name:
            filter_criteria.append(Collection.name.ilike(glob_to_sql(collection_name)))
        return self.session.query(Keyword)\
            .join(Keyword.collection)\
            .filter(*filter_criteria) \
            .order_by(Keyword.name) \
            .offset(skip)\
            .limit(limit) \
            .all()
