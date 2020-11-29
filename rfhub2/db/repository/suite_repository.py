import json
from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import func

from rfhub2.db.base import Suite, SuiteRel, TestCase
from rfhub2.model import KeywordRef, Suite as ModelSuite
from rfhub2.db.repository.base_repository import BaseRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.query_utils import glob_to_sql


class SuiteRepository(BaseRepository):
    @property
    def _items(self) -> Query:
        return self.items(parent_id=None)

    def get(self, item_id: int) -> Optional[ModelSuite]:
        result = self._items.filter(Suite.id == item_id).first()
        if result:
            return self.from_row(result)

    @staticmethod
    def filter_criteria(
        pattern: Optional[str], root_only: bool, use_doc: bool, use_tags: bool
    ):
        filter_criteria = []
        if pattern:
            if use_tags:
                filter_criteria.append(Suite.tags.ilike(glob_to_sql(pattern)))
            else:
                filter_criteria.append(Suite.name.ilike(glob_to_sql(pattern)))
            if use_doc:
                filter_criteria = [
                    or_(filter_criteria[0], Suite.doc.ilike(glob_to_sql(pattern)))
                ]
        if root_only:
            filter_criteria.append(Suite.is_root.is_(True))
        return filter_criteria

    def get_all(
        self,
        *,
        pattern: Optional[str] = None,
        parent_id: Optional[int] = None,
        root_only: bool = False,
        use_doc: bool = True,
        use_tags: bool = False,
        skip: int = 0,
        limit: int = 100,
        ordering: List[OrderingItem] = None,
    ) -> List[ModelSuite]:
        return [
            self.from_row(row)
            for row in (
                self.items(parent_id)
                .filter(*self.filter_criteria(pattern, root_only, use_doc, use_tags))
                .order_by(*Suite.ordering_criteria(ordering))
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def items(self, parent_id: Optional[int] = None):
        test_counts = (
            self.session.query(
                SuiteRel.parent_id.label("suite_id"),
                func.count(TestCase.id).label("test_count"),
            )
            .outerjoin(SuiteRel, TestCase.suite_id == SuiteRel.child_id)
            .group_by(SuiteRel.parent_id)
            .subquery()
        )
        parents = (
            self.session.query(SuiteRel.parent_id, SuiteRel.child_id)
            .filter(SuiteRel.degree == 1)
            .subquery()
        )
        query = (
            self.session.query(
                Suite, parents.c.parent_id, func.coalesce(test_counts.c.test_count, 0)
            )
            .outerjoin(parents, Suite.id == parents.c.child_id)
            .outerjoin(test_counts, Suite.id == test_counts.c.suite_id)
        )
        if parent_id:
            query = query.filter(parents.c.parent_id == parent_id)
        return query

    @staticmethod
    def from_row(row: Tuple[Suite, Optional[int], int]) -> ModelSuite:
        suite = row[0]
        return ModelSuite(
            id=suite.id,
            name=suite.name,
            longname=suite.longname,
            doc=suite.doc,
            is_root=suite.is_root,
            parent_id=row[1],
            test_count=row[2],
            keywords=SuiteRepository.from_keywords_json(suite.keywords),
        )

    @staticmethod
    def from_keywords_json(json_list: Optional[str]) -> List[KeywordRef]:
        return [KeywordRef(**d) for d in json.loads(json_list)] if json_list else []
