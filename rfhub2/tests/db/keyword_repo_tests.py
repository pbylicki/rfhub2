from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from rfhub2.db.base import Keyword
from rfhub2.db.session import db_session
from rfhub2.tests.db.base_repo_tests import BaseRepositoryTest


class KeywordRepositoryTest(BaseRepositoryTest):

    def test_should_add_keyword_with_collection_id(self) -> None:
        name_to_add = "test_keyword"
        keyword = Keyword(name=name_to_add, collection_id=self.collections[-1].id)
        self.keyword_repo.add(keyword)
        results: List[Keyword] = db_session.query(Keyword).filter_by(name=name_to_add).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, name_to_add)
        self.assertIsNotNone(results[0].id)
        self.assertEqual(results[0].collection, self.collections[-1])

    def test_should_not_add_keyword_without_collection_id(self) -> None:
        name_to_add = "test_keyword"
        keyword = Keyword(name=name_to_add)
        self.assertRaises(IntegrityError, lambda: self.keyword_repo.add(keyword))

    def test_should_get_keyword_by_id(self) -> None:
        result: Optional[Keyword] = self.keyword_repo.get(self.keywords[-1].id)
        self.assertEqual(result, self.keywords[-1])
        self.assertEqual(result.collection, self.collections[0])

    def test_should_get_all_keywords(self) -> None:
        result: List[Keyword] = self.keyword_repo.get_all()
        self.assertEqual(result, self.keywords)

    def test_should_filter_keywords_by_name_and_doc(self) -> None:
        test_data = [
            ("Environ", [self.keywords[0], self.keywords[2]]),
            ("some_key", self.keywords[1:2]),
            ("Teardown", [self.keywords[0], self.keywords[2]]),
            ("", self.keywords)
        ]
        for pattern, expected in test_data:
            with self.subTest(pattern=pattern, expected=expected):
                result: List[Keyword] = self.keyword_repo.get_all(pattern=pattern)
                self.assertEqual(result, expected)

    def test_should_filter_keywords_by_name_only(self) -> None:
        test_data = [
            ("Environ", []),
            ("some_key", self.keywords[1:2]),
            ("Teardown", self.keywords[2:]),
            ("", self.keywords)
        ]
        for pattern, expected in test_data:
            with self.subTest(pattern=pattern, expected=expected):
                result: List[Keyword] = self.keyword_repo.get_all(pattern=pattern, use_doc=False)
                self.assertEqual(result, expected)

    def test_should_get_all_keywords_with_limit(self) -> None:
        result: List[Keyword] = self.keyword_repo.get_all(limit=2)
        self.assertEqual(result, self.keywords[:2])

    def test_should_get_all_keywords_with_skip(self) -> None:
        result: List[Keyword] = self.keyword_repo.get_all(skip=2)
        self.assertEqual(result, self.keywords[2:])
