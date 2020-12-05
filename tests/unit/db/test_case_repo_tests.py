from sqlalchemy.exc import IntegrityError

from rfhub2.db.base import Suite, TestCase
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.test_case_repository import TestCaseRepository
from rfhub2.db.session import db_session
from rfhub2.model import (
    KeywordRef,
    KeywordRefList,
    KeywordType,
    TagList,
    TestCaseUpdate,
)
from tests.unit.db.base_repo_tests import BaseRepositoryTest


class TestCaseRepositoryTest(BaseRepositoryTest):
    def setUp(self) -> None:
        db_session.rollback()
        db_session.query(TestCase).delete()
        db_session.query(Suite).delete()
        self.tc_repo = TestCaseRepository(db_session)

        self.keyword_refs = [
            KeywordRef(name="Login", args=["admin"], kw_type=KeywordType.SETUP)
        ]
        self.keyword_refs_json = (
            '[{"name": "Login", "args": ["admin"], "kw_type": "SETUP"}]'
        )
        self.empty_keywords = KeywordRefList.of([])
        self.suite_1 = Suite(
            name="Suite 1",
            longname="Suite 1",
            keywords=self.keyword_refs_json,
            metadata_items="[]",
            is_root=True,
            rpa=False,
        )
        self.suite_2 = Suite(
            name="Suite 2",
            longname="Suite 2",
            keywords="[]",
            metadata_items="[]",
            is_root=True,
            rpa=False,
        )
        self.suites = [self.suite_1, self.suite_2]

        db_session.add_all(self.suites)
        db_session.flush()
        for item in self.suites:
            db_session.refresh(item)

        self.tc_1 = TestCase(
            suite_id=self.suite_1.id,
            name="TC1",
            line=1,
            doc="doc",
            source="source",
            template="template",
            timeout="timeout",
            tags="[]",
            keywords="[]",
        )
        self.tc_2 = TestCase(
            suite_id=self.suite_2.id, name="TC2", line=1, tags="[]", keywords="[]"
        )
        self.tc_3 = TestCase(
            suite_id=self.suite_1.id, name="TC3", line=10, tags="[]", keywords="[]"
        )
        self.tc_4 = TestCase(
            suite_id=self.suite_1.id, name="TC4", line=30, tags="[]", keywords="[]"
        )
        self.tc_5 = TestCase(
            suite_id=self.suite_1.id, name="TC5", line=20, tags="[]", keywords="[]"
        )
        self.test_cases = [self.tc_1, self.tc_2, self.tc_3, self.tc_4, self.tc_5]
        db_session.add_all(self.test_cases)
        db_session.commit()

        self.model_tc_1 = TestCaseRepository.from_row((self.tc_1, self.suite_1))
        self.model_tc_2 = TestCaseRepository.from_row((self.tc_2, self.suite_2))
        self.model_tc_3 = TestCaseRepository.from_row((self.tc_3, self.suite_1))
        self.model_tc_4 = TestCaseRepository.from_row((self.tc_4, self.suite_1))
        self.model_tc_5 = TestCaseRepository.from_row((self.tc_5, self.suite_1))
        self.model_tcs = [
            self.model_tc_1,
            self.model_tc_2,
            self.model_tc_3,
            self.model_tc_4,
            self.model_tc_5,
        ]

        self.tc_to_add = TestCase(
            suite_id=self.suite_2.id, name="TC_NEW", line=10, tags="[]", keywords="[]"
        )
        self.tc_added = TestCase(
            id=6,
            suite_id=self.suite_2.id,
            name="TC_NEW",
            line=10,
            tags="[]",
            keywords="[]",
        )
        self.model_tc_to_add = TestCaseRepository.from_row(
            (self.tc_added, self.suite_2)
        )

        self.model_tc_update = TestCaseUpdate(
            name="updated",
            line=1,
            suite_id=self.suite_2.id,
            keywords=KeywordRefList.of(self.keyword_refs),
            tags=TagList.of(["disabled"]),
        )
        self.model_tc_updated = self.model_tc_2.copy(
            update={
                "name": "updated",
                "longname": "Suite 2.updated",
                "keywords": KeywordRefList.of(self.keyword_refs),
                "tags": TagList.of(["disabled"]),
            }
        )

    def test_should_get_test_case_by_id(self) -> None:
        result = self.tc_repo.get(self.tc_1.id)
        self.assertEqual(result, self.model_tc_1)

    def test_should_get_none_for_nonexistent_id(self) -> None:
        result = self.tc_repo.get(9999)
        self.assertIsNone(result)

    def test_should_get_all_test_cases(self) -> None:
        result = self.tc_repo.get_all()
        self.assertEqual(result, self.model_tcs)

    def test_should_get_all_test_cases_by_suite_id(self) -> None:
        result = self.tc_repo.get_all(suite_id=self.suite_1.id)
        self.assertEqual(result, [self.model_tc_1] + self.model_tcs[2:])

    def test_should_get_all_test_cases_with_limit_and_skip(self) -> None:
        result = self.tc_repo.get_all(limit=2, skip=2)
        self.assertEqual(result, [self.model_tc_3, self.model_tc_4])

    def test_should_get_all_test_cases_with_pattern(self) -> None:
        result = self.tc_repo.get_all(pattern="C3")
        self.assertEqual(result, [self.model_tc_3])

    def test_should_get_all_test_cases_ordered_by_line_number(self) -> None:
        result = self.tc_repo.get_all(
            suite_id=self.suite_1.id, ordering=[OrderingItem("line")]
        )
        self.assertEqual(
            result, [self.model_tc_1, self.model_tc_3, self.model_tc_5, self.model_tc_4]
        )

    def test_should_add_test_case(self) -> None:
        result = self.tc_repo.add(self.tc_to_add)
        self.assertEqual(result, self.tc_to_add)
        suites = self.tc_repo.get_all()
        self.assertEqual(suites, self.model_tcs + [self.model_tc_to_add])

    def test_should_fail_to_add_test_case_with_invalid_suite_id(self) -> None:
        self.tc_to_add.suite_id = 999
        with self.assertRaises(IntegrityError):
            self.tc_repo.add(self.tc_to_add)
        db_session.rollback()
        result = self.tc_repo.get_all()
        self.assertEqual(result, self.model_tcs)

    def test_should_fail_to_add_duplicated_test_case_to_suite(self) -> None:
        self.tc_to_add.name = "TC2"
        with self.assertRaises(IntegrityError):
            self.tc_repo.add(self.tc_to_add)
        db_session.rollback()
        result = self.tc_repo.get_all()
        self.assertEqual(result, self.model_tcs)

    def test_should_update_test_case(self) -> None:
        result = self.tc_repo.update(self.tc_2, dict(self.model_tc_update))
        updated = self.tc_repo.get(self.tc_2.id)
        self.assertEqual(updated, self.model_tc_updated)

    def test_should_fail_to_update_test_case_to_duplicate(self) -> None:
        to_update = self.model_tc_update.copy(
            update={"name": "TC1", "suite_id": self.suite_1.id}
        )
        with self.assertRaises(IntegrityError):
            self.tc_repo.update(self.tc_2, dict(to_update))
        db_session.rollback()
        result = self.tc_repo.get_all()
        self.assertEqual(result, self.model_tcs)

    def test_should_fail_to_update_test_case_to_invalid_suite_id(self) -> None:
        to_update = self.model_tc_update.copy(update={"suite_id": 999})
        with self.assertRaises(IntegrityError):
            self.tc_repo.update(self.tc_2, dict(to_update))
        db_session.rollback()
        result = self.tc_repo.get_all()
        self.assertEqual(result, self.model_tcs)

    def test_should_delete_single_test_case(self) -> None:
        deleted = self.tc_repo.delete(self.tc_5.id)
        self.assertEqual(deleted, 1)
        suites = self.tc_repo.get_all()
        self.assertEqual(suites, self.model_tcs[:4])

    def test_delete_should_not_fail_for_nonexistent_id(self) -> None:
        deleted = self.tc_repo.delete(999)
        self.assertEqual(deleted, 0)
        suites = self.tc_repo.get_all()
        self.assertEqual(suites, self.model_tcs)
