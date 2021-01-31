from itertools import zip_longest
from typing import Dict, List, Optional, Tuple

from sqlalchemy import or_, Column
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import func
from sqlalchemy.orm.session import Session

from rfhub2.db.base import Suite, SuiteRel, TestCase
from rfhub2.model import (
    KeywordRefList,
    Suite as ModelSuite,
    SuiteHierarchy,
    SuiteHierarchyWithId,
    SuiteMetadata,
)
from rfhub2.db.repository.base_repository import BaseRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.query_utils import glob_to_sql


class SuiteRepository(BaseRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.test_counts = (
            self.session.query(
                SuiteRel.parent_id.label("suite_id"),
                func.count(TestCase.id).label("test_count"),
            )
            .outerjoin(SuiteRel, TestCase.suite_id == SuiteRel.child_id)
            .group_by(SuiteRel.parent_id)
            .subquery()
        )

    @property
    def _items(self) -> Query:
        return self.items(parent_id=None)

    @property
    def custom_column_mapping(self) -> Dict[str, Column]:
        return {"test_count": self.test_count_column}

    @property
    def test_count_column(self) -> Column:
        return func.coalesce(self.test_counts.c.test_count, 0)

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

    @staticmethod
    def from_row(row: Tuple[Suite, Optional[int], int]) -> ModelSuite:
        suite = row[0]
        return ModelSuite(
            id=suite.id,
            name=suite.name,
            longname=suite.longname,
            doc=suite.doc,
            source=suite.source,
            is_root=suite.is_root,
            rpa=suite.rpa,
            parent_id=row[1],
            test_count=row[2],
            keywords=KeywordRefList.parse_raw(suite.keywords),
            metadata=SuiteMetadata.parse_raw(suite.metadata_items),
        )

    def add_hierarchy(
        self, hierarchy: SuiteHierarchy
    ) -> Optional[SuiteHierarchyWithId]:
        try:
            hierarchies = self._add_suites([hierarchy], is_root=True)
            self._add_suite_rels(hierarchies, [])
            self.session.commit()
            return hierarchies[0]
        except Exception as e:
            self.session.rollback()
            raise e

    def delete_hierarchy(self, suite_id: int) -> int:
        suite_ids = (
            self.session.query(SuiteRel.child_id)
            .filter(SuiteRel.parent_id == suite_id)
            .subquery()
        )
        deleted = (
            self.session.query(Suite)
            .filter(Suite.id.in_(suite_ids))
            .delete(synchronize_session=False)
        )
        self.session.commit()
        return deleted

    def get(self, item_id: int) -> Optional[ModelSuite]:
        result = self._items.filter(Suite.id == item_id).first()
        if result:
            return self.from_row(result)

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
                .order_by(
                    *Suite.ordering_criteria(ordering, self.custom_column_mapping)
                )
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def items(self, parent_id: Optional[int] = None):
        parents = (
            self.session.query(SuiteRel.parent_id, SuiteRel.child_id)
            .filter(SuiteRel.degree == 1)
            .subquery()
        )
        query = (
            self.session.query(Suite, parents.c.parent_id, self.test_count_column)
            .outerjoin(parents, Suite.id == parents.c.child_id)
            .outerjoin(self.test_counts, Suite.id == self.test_counts.c.suite_id)
        )
        if parent_id:
            query = query.filter(parents.c.parent_id == parent_id)
        return query

    def _add_suites(
        self,
        hierarchies: List[SuiteHierarchy],
        is_root: bool,
        parent: Optional[SuiteHierarchyWithId] = None,
    ) -> List[SuiteHierarchyWithId]:
        if hierarchies:
            suites = [
                Suite.create(hierarchy, is_root, parent) for hierarchy in hierarchies
            ]
            self.session.add_all(suites)
            self.session.flush()
            hierarchies_with_id = [suite.to_hierarchy() for suite in suites]
            subhierarchies = [
                self._add_suites(h.suites, is_root=False, parent=h_id)
                for h, h_id in zip_longest(hierarchies, hierarchies_with_id)
            ]
            return [
                h.with_suites(ss)
                for h, ss in zip_longest(hierarchies_with_id, subhierarchies)
            ]
        else:
            return []

    def _add_suite_rels(
        self, hierarchies: List[SuiteHierarchyWithId], parents: List[int]
    ) -> None:
        for hierarchy in hierarchies:
            new_parents = [hierarchy.id] + parents
            self.session.add_all(
                [
                    SuiteRel(parent_id=parent, child_id=hierarchy.id, degree=degree)
                    for degree, parent in enumerate(new_parents)
                ]
            )
            self._add_suite_rels(hierarchy.suites, new_parents)
