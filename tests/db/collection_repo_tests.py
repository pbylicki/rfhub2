from typing import List, Optional

from rfhub2.db.base import Collection, Keyword
from rfhub2.db.session import db_session
from tests.db.base_repo_tests import BaseRepositoryTest


class CollectionRepositoryTest(BaseRepositoryTest):

    def test_should_add_collection(self) -> None:
        name_to_add = "test_collection"
        collection = Collection(name=name_to_add)
        self.collection_repo.add(collection)
        results: List[Collection] = db_session.query(Collection).filter_by(name=name_to_add).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, name_to_add)
        self.assertIsNotNone(results[0].id)

    def test_should_add_collection_with_keywords(self) -> None:
        name_to_add = "test_collection"
        collection = Collection(name=name_to_add)
        collection.keywords = [Keyword(name="Keyword1"), Keyword(name="Keyword2")]
        self.collection_repo.add(collection)
        results: List[Collection] = db_session.query(Collection).filter_by(name=name_to_add).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, name_to_add)
        self.assertIsNotNone(results[0].id)
        self.assertEqual(len(results[0].keywords), 2)
        self.assertEqual([k.name for k in results[0].keywords], ["Keyword1", "Keyword2"])

    def test_should_get_collection_by_id(self) -> None:
        result: Optional[Collection] = self.collection_repo.get(self.collections[-1].id)
        self.assertEqual(result, self.collections[-1])

    def test_should_get_collection_by_id_with_keywords(self) -> None:
        result: Optional[Collection] = self.collection_repo.get(self.collections[0].id)
        self.assertEqual(result, self.collections[0])
        self.assertEqual(result.keywords, self.collections[0].keywords)

    def test_should_get_all_collections(self) -> None:
        result: List[Collection] = self.collection_repo.get_all()
        self.assertEqual(result, self.collections)

    def test_should_get_all_collections_ordered_by_name(self) -> None:
        collection_a = Collection(name="A collection")
        collection_z = Collection(name="Z collection")
        self.collection_repo.add(collection_a)
        self.collection_repo.add(collection_z)
        result: List[Collection] = self.collection_repo.get_all()
        self.assertEqual(result, [collection_a] + self.collections + [collection_z])

    def test_should_filter_collections_by_name(self) -> None:
        test_data = [
            ("collection", self.collections[:2]),
            ("thir", self.collections[2:]),
            ("second collection", self.collections[1:2]),
            ("", self.collections)
        ]
        for pattern, expected in test_data:
            with self.subTest(pattern=pattern, expected=expected):
                result: List[Collection] = self.collection_repo.get_all(pattern=pattern)
                self.assertEqual(result, expected)

    def test_should_filter_collections_by_type(self) -> None:
        test_data = [
            ("Robo", self.collections[:2]),
            ("library", self.collections[2:]),
            ("", self.collections)
        ]
        for libtype, expected in test_data:
            with self.subTest(libtype=libtype, expected=expected):
                result: List[Collection] = self.collection_repo.get_all(libtype=libtype)
                self.assertEqual(result, expected)

    def test_should_get_all_collections_with_limit(self) -> None:
        result: List[Collection] = self.collection_repo.get_all(limit=2)
        self.assertEqual(result, self.collections[:2])

    def test_should_get_all_collections_with_skip(self) -> None:
        result: List[Collection] = self.collection_repo.get_all(skip=2)
        self.assertEqual(result, self.collections[2:])

    def test_should_delete_collection_with_keywords(self) -> None:
        result: int = self.collection_repo.delete(self.collections[0].id)
        self.assertEqual(result, 1)
        self.assertEqual(db_session.query(Collection).count(), 2)
        self.assertEqual(db_session.query(Keyword).count(), 1)

    def test_should_delete_collection_without_keywords(self) -> None:
        result: int = self.collection_repo.delete(self.collections[2].id)
        self.assertEqual(result, 1)
        self.assertEqual(db_session.query(Collection).count(), 2)
        self.assertEqual(db_session.query(Keyword).count(), 4)
