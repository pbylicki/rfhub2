from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.elements import BinaryExpression

from rfhub2.db.base import Suite, TestCase
from rfhub2.model import KeywordRefList, TagList, TestCase as ModelTestCase
from rfhub2.db.repository.base_repository import IdEntityRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.query_utils import glob_to_sql


class TestCaseRepository(IdEntityRepository):
    @property
    def _get_items(self) -> Query:
        return self.session.query(TestCase, Suite).filter(TestCase.suite_id == Suite.id)

    @property
    def _items(self) -> Query:
        return self.session.query(TestCase)

    def _id_filter(self, item_id: int) -> BinaryExpression:
        return TestCase.id == item_id

    @staticmethod
    def filter_criteria(
        pattern: Optional[str], suite_id: Optional[int], use_doc: bool, use_tags: bool
    ):
        filter_criteria = []
        if pattern:
            if use_tags:
                filter_criteria.append(TestCase.tags.ilike(glob_to_sql(pattern)))
            else:
                filter_criteria.append(TestCase.name.ilike(glob_to_sql(pattern)))
            if use_doc:
                filter_criteria = [
                    or_(filter_criteria[0], TestCase.doc.ilike(glob_to_sql(pattern)))
                ]
        if suite_id:
            filter_criteria.append(TestCase.suite_id == suite_id)
        return filter_criteria

    @staticmethod
    def from_row(row: Tuple[TestCase, Suite]) -> ModelTestCase:
        tc = row[0]
        return ModelTestCase(
            id=tc.id,
            name=tc.name,
            longname=f"{row[1].longname}.{tc.name}",
            line=tc.line,
            suite=row[1].to_nested(),
            doc=tc.doc,
            source=tc.source,
            template=tc.template,
            timeout=tc.timeout,
            keywords=KeywordRefList.parse_raw(tc.keywords),
            tags=TagList.parse_raw(tc.tags),
        )

    def get(self, item_id: int) -> Optional[ModelTestCase]:
        row = self._get_items.filter(self._id_filter(item_id)).first()
        if row:
            return self.from_row(row)

    def get_all(
        self,
        *,
        pattern: Optional[str] = None,
        suite_id: Optional[int] = None,
        use_doc: bool = True,
        use_tags: bool = False,
        skip: int = 0,
        limit: int = 100,
        ordering: List[OrderingItem] = None,
    ) -> List[ModelTestCase]:
        return [
            self.from_row(row)
            for row in (
                self._get_items.filter(
                    *self.filter_criteria(pattern, suite_id, use_doc, use_tags)
                )
                .order_by(*TestCase.ordering_criteria(ordering))
                .offset(skip)
                .limit(limit)
                .all()
            )
        ]

    def update(self, item: TestCase, update_data: dict) -> TestCase:
        if "keywords" in update_data:
            update_data["keywords"] = update_data["keywords"].json()
        if "tags" in update_data:
            update_data["tags"] = update_data["tags"].json()
        return super().update(item, update_data)
