import copy
import responses
import unittest

from rfhub2.cli.keywords.keywords_importer import KeywordsImporter
from rfhub2.cli.api_client import Client
from .test_data import *


class KeywordsImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = FIXTURE_PATH
        self.client = Client("http://localhost:8000", "rfhub", "rfhub")
        self.rfhub_importer = KeywordsImporter(
            self.client,
            (self.fixture_path,),
            True,
            load_mode="insert",
            include="",
            exclude="",
        )

    def test_import_data(self):
        with responses.RequestsMock() as rsps:
            rfhub_importer = KeywordsImporter(
                self.client,
                (self.fixture_path / "LibWithInit",),
                True,
                load_mode="insert",
                include="",
                exclude="",
            )
            rsps.add(
                responses.GET,
                f"{self.client.api_url}/collections/",
                json=[],
                status=200,
                adding_headers={"Content-Type": "application/json"},
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/collections/",
                json={"name": "LibWithInit", "id": 2},
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/keywords/",
                json=KEYWORDS_2,
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            result = rfhub_importer.import_data()
            self.assertCountEqual(result, (1, 4), msg=f"{result}")

    def test_import_libraries_insert_mode(self):
        with responses.RequestsMock() as rsps:
            rfhub_importer = KeywordsImporter(
                self.client,
                (self.fixture_path / "LibWithInit",),
                True,
                load_mode="insert",
                include="",
                exclude="",
            )
            rsps.add(
                responses.GET,
                f"{self.client.api_url}/collections/",
                json=[],
                status=200,
                adding_headers={"Content-Type": "application/json"},
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/collections/",
                json={"name": "LibWithInit", "id": 2},
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/keywords/",
                json=KEYWORDS_2,
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            result = rfhub_importer.import_libraries()
            self.assertCountEqual(result, (1, 4), msg=f"{result}")

    def test_import_libraries_append_mode(self):
        with responses.RequestsMock() as rsps:
            rfhub_importer = KeywordsImporter(
                self.client,
                (self.fixture_path / "LibWithInit",),
                True,
                load_mode="append",
                include="",
                exclude="",
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/collections/",
                json={"name": "LibWithInit", "id": 2},
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/keywords/",
                json=KEYWORDS_2,
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            result = rfhub_importer.import_libraries()
            self.assertCountEqual(result, (1, 4), msg=f"{result}")

    def test_import_libraries_update_mode(self):
        with responses.RequestsMock() as rsps:
            rfhub_importer = KeywordsImporter(
                self.client,
                (self.fixture_path / "LibWithInit",),
                True,
                load_mode="update",
                include="",
                exclude="",
            )
            rsps.add(
                responses.GET,
                f"{self.client.api_url}/collections/",
                json=[],
                status=200,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/collections/",
                json={"name": "LibWithInit", "id": 2},
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/keywords/",
                json=KEYWORDS_2,
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            result = rfhub_importer.import_libraries()
            self.assertCountEqual(result, (1, 4), msg=f"{result}")

    def test_import_libraries_merge_mode(self):
        with responses.RequestsMock() as rsps:
            rfhub_importer = KeywordsImporter(
                self.client,
                (self.fixture_path / "LibWithInit",),
                True,
                load_mode="merge",
                include="",
                exclude="",
            )
            rsps.add(
                responses.GET,
                f"{self.client.api_url}/collections/",
                json=[],
                status=200,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/collections/",
                json={"name": "LibWithInit", "id": 2},
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/keywords/",
                json=KEYWORDS_2,
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            result = rfhub_importer.import_libraries()
            self.assertCountEqual(result, (1, 4), msg=f"{result}")

    def test_delete_all_collections(self):
        with responses.RequestsMock() as rsps:
            for i in [2, 2, 66, 66]:
                rsps.add(
                    responses.GET,
                    f"{self.client.api_url}/collections/",
                    json=[{"id": i}],
                    status=200,
                    adding_headers={"Content-Type": "application/json"},
                )
            rsps.add(
                responses.DELETE,
                f"{self.client.api_url}/collections/2/",
                status=204,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.DELETE,
                f"{self.client.api_url}/collections/66/",
                status=204,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.GET,
                f"{self.client.api_url}/collections/",
                json=[],
                status=200,
                adding_headers={"Content-Type": "application/json"},
            )
            result = self.rfhub_importer.delete_all_collections()
            self.assertEqual({2, 66}, result)

    def test_delete_collections(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{self.client.api_url}/collections/",
                json=[{"id": 2}, {"id": 66}],
                status=200,
                adding_headers={"Content-Type": "application/json"},
            )
            rsps.add(
                responses.DELETE,
                f"{self.client.api_url}/collections/2/",
                status=204,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.DELETE,
                f"{self.client.api_url}/collections/66/",
                status=204,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            result = self.rfhub_importer._delete_collections()
            self.assertEqual({2, 66}, result)

    def test_get_all_collections_should_return_all_collections(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{self.client.api_url}/collections/?skip=0&limit=999999",
                json=[
                    {
                        "id": 1,
                        "name": "SingleClassLib",
                        "keywords": [],
                        "type": "LIBRARY",
                        "doc_format": "ROBOT",
                        "scope": "TEST",
                        "version": "1.2.3",
                        "path": str(
                            FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py"
                        ),
                        "doc": "Overview that should be imported for SingleClassLib.",
                    }
                ],
                status=200,
                adding_headers={"Content-Type": "application/json"},
            )
            result = self.rfhub_importer.get_all_collections()
            existing_collection = copy.deepcopy(EXISTING_COLLECTION)
            existing_collection.keywords = []
            self.assertListEqual([existing_collection], result)

    def test_update_collections_should_insert_collections(self):
        existing_collections = [
            Collection(
                id=1,
                path="1",
                type="library",
                version="1",
                name="a",
                keywords=EXISTING_COLLECTION_KEYWORDS,
            ),
            Collection(
                id=2,
                path="2",
                type="library",
                version="2",
                name="b",
                keywords=EXISTING_COLLECTION_KEYWORDS,
            ),
            Collection(
                id=3,
                path="3",
                type="library",
                version="3",
                name="c",
                keywords=EXISTING_COLLECTION_KEYWORDS,
            ),
            Collection(
                id=4,
                path="4",
                type="resource",
                version="4",
                name="d",
                keywords=EXISTING_COLLECTION_KEYWORDS,
            ),
            Collection(
                id=5,
                path="5",
                type="resource",
                version="5",
                name="e",
                keywords=EXISTING_COLLECTION_KEYWORDS,
            ),
        ]
        new_collections = [
            CollectionUpdateWithKeywords(
                CollectionUpdate(name="a", path="1", type="library", version="2"),
                [EXPECTED_COLLECTION_KEYWORDS_1_3],
            ),
            CollectionUpdateWithKeywords(
                CollectionUpdate(name="b", path="2", type="library", version="3"),
                [EXPECTED_COLLECTION_KEYWORDS_1_3],
            ),
            CollectionUpdateWithKeywords(
                CollectionUpdate(name="c", path="3", type="library", version="4"),
                [EXPECTED_COLLECTION_KEYWORDS_1_3],
            ),
            CollectionUpdateWithKeywords(
                CollectionUpdate(name="d", path="4", type="resource", version=""),
                [EXPECTED_COLLECTION_KEYWORDS_1_3],
            ),
            CollectionUpdateWithKeywords(
                CollectionUpdate(name="e", path="5", type="resource", version=""),
                [EXPECTED_COLLECTION_KEYWORDS_1_3],
            ),
        ]
        with responses.RequestsMock() as rsps:
            for i in range(1, 5):
                rsps.add(
                    responses.POST,
                    f"{self.client.api_url}/collections/",
                    json=existing_collections[0].dict(),
                    status=201,
                    adding_headers={
                        "Content-Type": "application/json",
                        "accept": "application/json",
                    },
                )
                rsps.add(
                    responses.POST,
                    f"{self.client.api_url}/keywords/",
                    json=[EXPECTED_COLLECTION_KEYWORDS_1_3.dict()],
                    status=201,
                    adding_headers={
                        "Content-Type": "application/json",
                        "accept": "application/json",
                    },
                )
            result = self.rfhub_importer.update_collections(
                existing_collections, new_collections
            )
            self.assertCountEqual(EXPECTED_UPDATE_COLLECTIONS, result)

    def test_delete_outdated_collections_should_delete_outdated_collections(self):
        existing_collections = [
            Collection(id=1, path=1, type="library", version=1, name="a", keywords=[]),
            Collection(id=2, path=2, type="library", version=2, name="b", keywords=[]),
            Collection(id=3, path=3, type="library", version=3, name="c", keywords=[]),
        ]
        new_collections = [
            CollectionUpdateWithKeywords(
                CollectionUpdate(path=1, type="library", version=2, name="a"), []
            ),
            CollectionUpdateWithKeywords(
                CollectionUpdate(path=2, type="library", version=3, name="b"), []
            ),
            CollectionUpdateWithKeywords(
                CollectionUpdate(path=3, type="library", version=4, name="c"), []
            ),
        ]
        with responses.RequestsMock() as rsps:
            for i in range(1, 4):
                rsps.add(
                    responses.DELETE,
                    f"{self.client.api_url}/collections/{i}/",
                    status=204,
                    adding_headers={"accept": "application/json"},
                )
            result = self.rfhub_importer.delete_outdated_collections(
                existing_collections, new_collections
            )
            self.assertSetEqual({1, 2, 3}, result)

    def test_delete_outdated_collections_should_delete_outdated_collections_obsolete_false(
        self
    ):
        existing_collections = [
            Collection(id=1, path=1, type="library", version=1, name="a", keywords=[]),
            Collection(id=2, path=2, type="library", version=2, name="b", keywords=[]),
            Collection(id=3, path=3, type="library", version=3, name="c", keywords=[]),
            Collection(id=4, path=4, type="library2", version=3, name="d", keywords=[]),
        ]
        new_collections = [
            CollectionUpdateWithKeywords(
                CollectionUpdate(path=1, type="library", version=2, name="a"), []
            ),
            CollectionUpdateWithKeywords(
                CollectionUpdate(path=2, type="library", version=3, name="b"), []
            ),
            CollectionUpdateWithKeywords(
                CollectionUpdate(path=3, type="library", version=4, name="c"), []
            ),
        ]
        with responses.RequestsMock() as rsps:
            for i in range(1, 4):
                rsps.add(
                    responses.DELETE,
                    f"{self.client.api_url}/collections/{i}/",
                    status=204,
                    adding_headers={"accept": "application/json"},
                )
            result = self.rfhub_importer.delete_outdated_collections(
                existing_collections, new_collections, False
            )
            self.assertSetEqual({1, 2, 3}, result)

    def test_add_collections_should_return_loaded_collections_and_keywords_number(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/collections/",
                json=EXISTING_COLLECTION.dict(),
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/keywords/",
                json=[EXPECTED_COLLECTION_KEYWORDS_2_1.json()],
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            result = self.rfhub_importer.add_collections(
                [EXPECTED_COLLECTION_WITH_KW_2]
            )
            self.assertCountEqual(result, EXPECTED_ADD_COLLECTIONS)

    def test_add_collections_should_exit_when_unauthorized(self):
        with self.assertRaises(StopIteration) as cm:
            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.POST,
                    f"{self.client.api_url}/collections/",
                    json={"detail": "Unauthorized to perform this action"},
                    status=401,
                    adding_headers={
                        "Content-Type": "application/json",
                        "accept": "application/json",
                    },
                )
                self.rfhub_importer.add_collections([EXPECTED_COLLECTION_WITH_KW_2])

    def test_collection_path_and_name_match_should_return_true_when_matched(self):
        result = KeywordsImporter._collection_path_and_name_match(
            EXPECTED_COLLECTION, EXPECTED_COLLECTION
        )
        self.assertTrue(result)

    def test_collection_path_and_name_match_should_return_false_when_not_matched(self):
        result = KeywordsImporter._collection_path_and_name_match(
            EXPECTED_COLLECTION_WITH_KW_1.collection, EXISTING_COLLECTION_2
        )
        self.assertFalse(result)

    def test_get_collections_to_update_should_return_collections_to_update(self):
        existing_collections = copy.deepcopy(
            [EXISTING_COLLECTION, EXISTING_COLLECTION_2]
        )
        new_collections = copy.deepcopy(
            [EXPECTED_COLLECTION_WITH_KW_1, EXPECTED_COLLECTION_WITH_KW_2]
        )
        new_collections[0].collection.version = "1.2.4"
        new_collections[1].collection.version = "3.3.0"
        result = KeywordsImporter._get_collections_to_update(
            existing_collections, new_collections
        )
        self.assertListEqual(new_collections, result)

    def test_get_new_collections_should_return_only_new_collections(self):
        exisitng_collections = copy.deepcopy([EXISTING_COLLECTION])
        new_collections = copy.deepcopy(
            [EXPECTED_COLLECTION_WITH_KW_1, EXPECTED_COLLECTION_WITH_KW_2]
        )
        result = KeywordsImporter._get_new_collections(
            exisitng_collections, new_collections
        )
        self.assertListEqual([EXPECTED_COLLECTION_WITH_KW_2], result)

    def test_library_or_resource_changed_should_return_false_when_library_unchanged(
        self
    ):
        result = KeywordsImporter._library_or_resource_changed(
            EXPECTED_COLLECTION_WITH_KW_1, EXISTING_COLLECTION
        )
        self.assertFalse(result)

    def test_library_or_resource_changed_should_return_true_when_library_changed(self):
        collection2 = copy.deepcopy(EXPECTED_COLLECTION)
        collection2.version = "1.2.4"
        result = KeywordsImporter._library_or_resource_changed(
            EXPECTED_COLLECTION_WITH_KW_1, EXISTING_COLLECTION_2
        )
        self.assertTrue(result)

    def test_library_or_resource_changed_should_return_false_when_resource_unchanged(
        self
    ):
        expected_collection = copy.deepcopy(EXPECTED_COLLECTION)
        existing_collection = copy.deepcopy(EXISTING_COLLECTION)
        expected_collection.type = "resource"
        existing_collection.type = "resource"
        result = KeywordsImporter._library_or_resource_changed(
            EXPECTED_COLLECTION_WITH_KW_1, EXISTING_COLLECTION
        )
        self.assertFalse(result)

    def test_library_or_resource_changed_should_return_true_when_resource_changed(self):
        EXPECTED_COLLECTION.type = "resource"
        EXISTING_COLLECTION.type = "resource"
        EXISTING_COLLECTION.doc = "abc"
        result = KeywordsImporter._library_or_resource_changed(
            EXPECTED_COLLECTION_WITH_KW_1, EXISTING_COLLECTION
        )
        self.assertTrue(result)
