from sqlalchemy.exc import IntegrityError

from rfhub2.db.base import Suite, SuiteRel, TestCase
from rfhub2.db.repository.suite_repository import SuiteRepository
from rfhub2.db.session import db_session
from rfhub2.model import (
    KeywordRef,
    KeywordRefList,
    KeywordType,
    MetadataItem,
    Suite as ModelSuite,
    SuiteHierarchy,
    SuiteMetadata,
)
from tests.unit.db.base_repo_tests import BaseRepositoryTest


class SuiteRepositoryTest(BaseRepositoryTest):
    def setUp(self) -> None:
        db_session.rollback()
        db_session.query(TestCase).delete()
        db_session.query(SuiteRel).delete()
        db_session.query(Suite).delete()
        self.suite_repo = SuiteRepository(db_session)

        self.keyword_refs = [
            KeywordRef(name="Login", args=["admin"], kw_type=KeywordType.SETUP)
        ]
        self.keyword_refs_json = (
            '[{"name": "Login", "args": ["admin"], "kw_type": "SETUP"}]'
        )
        self.empty_keywords = KeywordRefList.of([])
        self.metadata_items = [MetadataItem(key="version", value="1.0")]
        self.metadata_items_json = '[{"key": "version", "value": "1.0"}]'
        self.empty_metadata = SuiteMetadata.of([])
        self.suite_1 = Suite(
            name="Suite 1",
            longname="Suite 1",
            keywords=self.keyword_refs_json,
            metadata_items=self.metadata_items_json,
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
        self.suite_3 = Suite(
            name="Suite 3",
            longname="Suite 3",
            keywords="[]",
            metadata_items="[]",
            is_root=True,
            rpa=False,
        )
        self.suite_11 = Suite(
            name="Suite 1-1",
            longname="Suite 1.Suite 1-1",
            keywords="[]",
            metadata_items="[]",
            is_root=False,
            rpa=False,
        )
        self.suite_12 = Suite(
            name="Suite 1-2",
            longname="Suite 1.Suite 1-2",
            keywords="[]",
            metadata_items="[]",
            is_root=False,
            rpa=False,
        )
        self.suite_111 = Suite(
            name="Suite 1-1-1",
            longname="Suite 1.Suite 1-1.Suite 1-1-1",
            keywords="[]",
            metadata_items="[]",
            is_root=False,
            rpa=False,
        )
        self.suite_112 = Suite(
            name="Suite 1-1-2",
            longname="Suite 1.Suite 1-1.Suite 1-1-2",
            keywords="[]",
            metadata_items="[]",
            is_root=False,
            rpa=False,
        )
        self.suite_121 = Suite(
            name="Suite 1-2-1",
            longname="Suite 1.Suite 1-2.Suite 1-2-1",
            keywords="[]",
            metadata_items="[]",
            is_root=False,
            rpa=False,
        )
        self.suites = [
            self.suite_1,
            self.suite_2,
            self.suite_3,
            self.suite_11,
            self.suite_12,
            self.suite_111,
            self.suite_112,
            self.suite_121,
        ]

        db_session.add_all(self.suites)
        db_session.flush()
        for item in self.suites:
            db_session.refresh(item)

        self.suite_rels = [
            SuiteRel(parent_id=self.suite_1.id, child_id=self.suite_1.id, degree=0),
            SuiteRel(parent_id=self.suite_1.id, child_id=self.suite_11.id, degree=1),
            SuiteRel(parent_id=self.suite_1.id, child_id=self.suite_12.id, degree=1),
            SuiteRel(parent_id=self.suite_1.id, child_id=self.suite_111.id, degree=2),
            SuiteRel(parent_id=self.suite_1.id, child_id=self.suite_112.id, degree=2),
            SuiteRel(parent_id=self.suite_1.id, child_id=self.suite_121.id, degree=2),
            SuiteRel(parent_id=self.suite_11.id, child_id=self.suite_11.id, degree=0),
            SuiteRel(parent_id=self.suite_11.id, child_id=self.suite_111.id, degree=1),
            SuiteRel(parent_id=self.suite_11.id, child_id=self.suite_112.id, degree=1),
            SuiteRel(parent_id=self.suite_12.id, child_id=self.suite_12.id, degree=0),
            SuiteRel(parent_id=self.suite_12.id, child_id=self.suite_121.id, degree=1),
            SuiteRel(parent_id=self.suite_111.id, child_id=self.suite_111.id, degree=0),
            SuiteRel(parent_id=self.suite_112.id, child_id=self.suite_112.id, degree=0),
            SuiteRel(parent_id=self.suite_121.id, child_id=self.suite_121.id, degree=0),
            SuiteRel(parent_id=self.suite_2.id, child_id=self.suite_2.id, degree=0),
            SuiteRel(parent_id=self.suite_3.id, child_id=self.suite_3.id, degree=0),
        ]
        self.test_cases = [
            TestCase(
                suite_id=self.suite_2.id, name="TC2", line=1, tags="[]", keywords="[]"
            ),
            TestCase(
                suite_id=self.suite_111.id, name="TC1", line=1, tags="[]", keywords="[]"
            ),
            TestCase(
                suite_id=self.suite_111.id, name="TC3", line=1, tags="[]", keywords="[]"
            ),
            TestCase(
                suite_id=self.suite_112.id, name="TC4", line=1, tags="[]", keywords="[]"
            ),
            TestCase(
                suite_id=self.suite_121.id, name="TC5", line=1, tags="[]", keywords="[]"
            ),
        ]
        db_session.add_all(self.suite_rels)
        db_session.add_all(self.test_cases)
        db_session.commit()

        # model instances
        self.model_suite_1 = SuiteRepository.from_row((self.suite_1, None, 4))
        self.model_suite_11 = SuiteRepository.from_row(
            (self.suite_11, self.suite_1.id, 3)
        )
        self.model_suite_111 = SuiteRepository.from_row(
            (self.suite_111, self.suite_11.id, 2)
        )
        self.model_suite_112 = SuiteRepository.from_row(
            (self.suite_112, self.suite_11.id, 1)
        )
        self.model_suite_12 = SuiteRepository.from_row(
            (self.suite_12, self.suite_1.id, 1)
        )
        self.model_suite_121 = SuiteRepository.from_row(
            (self.suite_121, self.suite_12.id, 1)
        )
        self.model_suite_2 = SuiteRepository.from_row((self.suite_2, None, 1))
        self.model_suite_3 = SuiteRepository.from_row((self.suite_3, None, 0))

        self.model_suites = [
            self.model_suite_1,
            self.model_suite_11,
            self.model_suite_111,
            self.model_suite_112,
            self.model_suite_12,
            self.model_suite_121,
            self.model_suite_2,
            self.model_suite_3,
        ]

        self.hierarchy_d = SuiteHierarchy(
            name="d",
            keywords=self.empty_keywords,
            metadata=self.empty_metadata,
            suites=[],
        )
        self.hierarchy_e = SuiteHierarchy(
            name="e",
            keywords=self.empty_keywords,
            metadata=self.empty_metadata,
            suites=[],
        )
        self.hierarchy_b = SuiteHierarchy(
            name="b",
            keywords=self.empty_keywords,
            metadata=self.empty_metadata,
            suites=[self.hierarchy_d, self.hierarchy_e],
        )
        self.hierarchy_c = SuiteHierarchy(
            name="c",
            keywords=self.empty_keywords,
            metadata=self.empty_metadata,
            suites=[],
        )
        self.hierarchy_a = SuiteHierarchy(
            name="a",
            doc="doc",
            source="/path",
            keywords=KeywordRefList.of(self.keyword_refs),
            metadata=self.empty_metadata,
            suites=[self.hierarchy_b, self.hierarchy_c],
            rpa=True,
        )

        self.model_suite_a = ModelSuite(
            id=9,
            name="a",
            longname="a",
            doc="doc",
            source="/path",
            is_root=True,
            rpa=True,
            test_count=0,
            keywords=KeywordRefList.of(self.keyword_refs),
            metadata=self.empty_metadata,
        )
        self.model_suite_b = ModelSuite(
            id=10,
            name="b",
            longname="a.b",
            is_root=False,
            parent_id=9,
            test_count=0,
            keywords=self.empty_keywords,
            metadata=self.empty_metadata,
        )
        self.model_suite_c = ModelSuite(
            id=11,
            name="c",
            longname="a.c",
            is_root=False,
            parent_id=9,
            test_count=0,
            keywords=self.empty_keywords,
            metadata=self.empty_metadata,
        )
        self.model_suite_d = ModelSuite(
            id=12,
            name="d",
            longname="a.b.d",
            is_root=False,
            parent_id=10,
            test_count=0,
            keywords=self.empty_keywords,
            metadata=self.empty_metadata,
        )
        self.model_suite_e = ModelSuite(
            id=13,
            name="e",
            longname="a.b.e",
            is_root=False,
            parent_id=10,
            test_count=0,
            keywords=self.empty_keywords,
            metadata=self.empty_metadata,
        )
        self.model_suites_added = [
            self.model_suite_a,
            self.model_suite_b,
            self.model_suite_d,
            self.model_suite_e,
            self.model_suite_c,
        ]

    def test_should_get_suite_by_id(self) -> None:
        result = self.suite_repo.get(self.suite_2.id)
        self.assertEqual(result, self.model_suite_2)

    def test_should_get_none_for_nonexistent_id(self) -> None:
        result = self.suite_repo.get(9999)
        self.assertIsNone(result)

    def test_should_get_all_suites(self) -> None:
        result = self.suite_repo.get_all()
        self.assertEqual(result, self.model_suites)

    def test_should_get_all_suites_by_parent_id(self) -> None:
        result = self.suite_repo.get_all(parent_id=self.suite_1.id)
        self.assertEqual(result, [self.model_suite_11, self.model_suite_12])

    def test_should_get_only_root_suites(self) -> None:
        result = self.suite_repo.get_all(root_only=True)
        self.assertEqual(
            result, [self.model_suite_1, self.model_suite_2, self.model_suite_3]
        )

    def test_should_get_all_suites_with_limit_and_skip(self) -> None:
        result = self.suite_repo.get_all(limit=2, skip=4)
        self.assertEqual(result, [self.model_suite_12, self.model_suite_121])

    def test_should_get_all_suites_with_pattern(self) -> None:
        result = self.suite_repo.get_all(pattern="1-2")
        self.assertEqual(
            result, [self.model_suite_112, self.model_suite_12, self.model_suite_121]
        )

    def test_should_add_nested_suite_hierarchy(self) -> None:
        self.suite_repo.add_hierarchy(self.hierarchy_a)
        suites = self.suite_repo.get_all()
        self.assertEqual(suites, self.model_suites + self.model_suites_added)

    def test_should_add_single_suite_hierarchy(self) -> None:
        hierarchy = self.hierarchy_a.copy(update={"suites": []})
        self.suite_repo.add_hierarchy(hierarchy)
        suites = self.suite_repo.get_all()
        self.assertEqual(suites, self.model_suites + [self.model_suite_a])

    def test_should_rollback_when_adding_suite_hierarchy_fails(self) -> None:
        suite = Suite.create(self.hierarchy_e)
        suite.longname = "a.b.e"
        db_session.add(suite)
        db_session.commit()
        with self.assertRaises(IntegrityError):
            self.suite_repo.add_hierarchy(self.hierarchy_a)
        suites = self.suite_repo.get_all()
        self.assertEqual(
            suites,
            self.model_suites
            + [
                self.model_suite_e.copy(
                    update={"id": 9, "is_root": True, "parent_id": None}
                )
            ],
        )

    def test_should_delete_single_suite_with_no_test_cases(self) -> None:
        deleted = self.suite_repo.delete_hierarchy(self.suite_3.id)
        self.assertEqual(deleted, 1)
        suites = self.suite_repo.get_all()
        self.assertEqual(suites, self.model_suites[:7])

    def test_should_delete_single_suite_and_related_test_cases(self) -> None:
        deleted = self.suite_repo.delete_hierarchy(self.suite_2.id)
        self.assertEqual(deleted, 1)
        suites = self.suite_repo.get_all()
        self.assertEqual(suites, self.model_suites[:6] + [self.model_suite_3])

    def test_should_delete_suite_hierarchy_and_related_test_cases(self) -> None:
        deleted = self.suite_repo.delete_hierarchy(self.suite_11.id)
        self.assertEqual(deleted, 3)
        suites = self.suite_repo.get_all()
        self.assertEqual(
            suites,
            [
                self.model_suite_1.copy(update={"test_count": 1}),
                self.model_suite_12,
                self.model_suite_121,
                self.model_suite_2,
                self.model_suite_3,
            ],
        )

    def test_delete_should_not_fail_for_nonexistent_id(self) -> None:
        deleted = self.suite_repo.delete_hierarchy(999)
        self.assertEqual(deleted, 0)
        suites = self.suite_repo.get_all()
        self.assertEqual(suites, self.model_suites)
