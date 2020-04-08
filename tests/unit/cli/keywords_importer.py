import copy
import responses
import unittest
from pathlib import Path
from robot.libdocpkg import LibraryDocumentation
import robot.libraries

from rfhub2.cli.keywords_importer import CollectionUpdateWithKeywords, KeywordsImporter
from rfhub2.cli.api_client import Client
from rfhub2.model import Collection, CollectionUpdate, KeywordUpdate, NestedKeyword

FIXTURE_PATH = Path.cwd() / "tests" / "fixtures" / "initial"
STATISTICS_PATH = FIXTURE_PATH / ".." / "statistics"
EXPECTED_LIBDOC = {
    "doc": "Documentation for library ``Test Libdoc File``.",
    "doc_format": "ROBOT",
    "name": "Test Libdoc File",
    "scope": "global",
    "type": "library",
    "version": "3.2.0",
    "keywords": [{"name": "Someone Shall Pass", "args": '["who"]', "doc": ""}],
}
EXPECTED_INIT_DOC = """\n\nHere goes some docs that should appear on rfhub2 if init is parametrised
\nThe library import:
\nExamples:
| Library    LibWithInit   dummy=../one               # add one dummy
| Library    LibWithInit   path=../one,/global        # add two dummies"""
EXPECTED_KEYWORDS = [
    KeywordUpdate(
        args="",
        doc="This keyword was imported from file\n"
        "with .resource extension, available since RFWK 3.1",
        name="Keyword 1 Imported From Resource File",
        tags=["first_tag"],
    ),
    KeywordUpdate(
        args='["arg_1", "arg_2"]',
        doc="This keyword was imported from file\n"
        "with .resource extension, available since RFWK 3.1",
        name="Keyword 2 Imported From Resource File",
        tags=["first_tag", "second_tag"],
    ),
]
EXPECTED_TRAVERSE_PATHS_INIT = {FIXTURE_PATH / "LibWithInit"}
EXPECTED_TRAVERSE_PATHS_NO_INIT = {
    FIXTURE_PATH / "LibsWithEmptyInit" / "LibWithEmptyInit1.py",
    FIXTURE_PATH / "LibsWithEmptyInit" / "LibWithEmptyInit2.py",
}
EXPECTED_GET_LIBRARIES = (
    EXPECTED_TRAVERSE_PATHS_INIT
    | EXPECTED_TRAVERSE_PATHS_NO_INIT
    | {
        FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py",
        FIXTURE_PATH / "test_libdoc_file.xml",
        FIXTURE_PATH / "test_resource.resource",
        FIXTURE_PATH / "test_robot.robot",
        FIXTURE_PATH / "arg_parse.py",
        FIXTURE_PATH / "data_error.py",
        FIXTURE_PATH / "LibWithInit" / "test_res_lib_dir.resource",
    }
)
EXPECTED_GET_EXECUTION_PATHS = {
    STATISTICS_PATH / "output.xml",
    STATISTICS_PATH / "subdir" / "output.xml",
}
EXPECTED_COLLECTION = CollectionUpdate(
    doc="Overview that should be imported for SingleClassLib.",
    doc_format="ROBOT",
    name="SingleClassLib",
    path=str(FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py"),
    scope="test case",
    type="library",
    version="1.2.3",
)

EXPECTED_COLLECTION_KEYWORDS_1_1 = KeywordUpdate(
    args="",
    doc="Docstring for single_class_lib_method_1",
    name="Single Class Lib Method 1",
    tags=["tag_1", "tag_2"],
)
EXPECTED_COLLECTION_KEYWORDS_1_2 = KeywordUpdate(
    args="",
    doc="Docstring for single_class_lib_method_2",
    name="Single Class Lib Method 2",
    tags=[],
)
EXPECTED_COLLECTION_KEYWORDS_1_3 = KeywordUpdate(
    args='["param_1", "param_2"]',
    doc="Docstring for single_class_lib_method_3 with two params",
    name="Single Class Lib Method 3",
    tags=[],
)
EXPECTED_COLLECTION_KEYWORDS_1 = [
    EXPECTED_COLLECTION_KEYWORDS_1_1,
    EXPECTED_COLLECTION_KEYWORDS_1_2,
    EXPECTED_COLLECTION_KEYWORDS_1_3,
]
EXISTING_COLLECTION_KEYWORDS = [
    NestedKeyword(**{**EXPECTED_COLLECTION_KEYWORDS_1_3.dict(), "id": 1})
]
EXISTING_COLLECTION = Collection(
    **{
        **EXPECTED_COLLECTION.dict(),
        "id": 1,
        "keywords": [
            NestedKeyword(**{**EXPECTED_COLLECTION_KEYWORDS_1_3.dict(), "id": 1})
        ],
    }
)
EXPECTED_COLLECTION_2 = CollectionUpdate(
    doc="Documentation for library ``Test Libdoc File``.",
    doc_format="ROBOT",
    name="Test Libdoc File",
    path=str(FIXTURE_PATH / "test_libdoc_file.xml"),
    scope="global",
    type="library",
    version="3.2.0",
)
EXPECTED_COLLECTION_KEYWORDS_2_1 = KeywordUpdate(
    args='["who"]', doc="", name="Someone Shall Pass", tags=[]
)
EXPECTED_COLLECTION_KEYWORDS_2 = [EXPECTED_COLLECTION_KEYWORDS_2_1]
EXISTING_COLLECTION_2 = Collection(
    **{
        **EXPECTED_COLLECTION_2.dict(),
        "id": 1,
        "keywords": [
            NestedKeyword(**{**EXPECTED_COLLECTION_KEYWORDS_2_1.dict(), "id": 1})
        ],
    }
)
EXPECTED_ADD_COLLECTIONS = [{"name": "Test Libdoc File", "keywords": 1}]
EXPECTED_UPDATE_COLLECTIONS = [
    {"name": "a", "keywords": 1},
    {"name": "b", "keywords": 1},
    {"name": "c", "keywords": 1},
    {"name": "d", "keywords": 1},
    {"name": "e", "keywords": 1},
]
KEYWORDS_1 = [
    {
        "args": "",
        "doc": "Docstring for single_class_lib_method_1",
        "name": "Single Class Lib Method 1",
    },
    {
        "args": "",
        "doc": "Docstring for single_class_lib_method_2",
        "name": "Single Class Lib Method 2",
    },
    {
        "args": '["param_1", "param_2"]',
        "doc": "Docstring for single_class_lib_method_3 with two params",
        "name": "Single Class Lib Method 3",
    },
]
KEYWORDS_2 = [{"args": '["who"]', "doc": "", "name": "Someone Shall Pass"}]
KEYWORDS_EXTENDED = [
    {
        "args": "",
        "doc": "Docstring for single_class_lib_method_1",
        "name": "Single Class Lib Method 1",
        "id": 15,
        "synopsis": "Docstring for lib_with_empty_init_1_method_1",
        "html_doc": "<p>Docstring for lib_with_empty_init_1_method_1</p>",
        "arg_string": "",
    },
    {
        "args": "",
        "doc": "Docstring for single_class_lib_method_2",
        "name": "Single Class Lib Method 2",
        "id": 16,
        "synopsis": "Docstring for lib_with_empty_init_1_method_1",
        "html_doc": "<p>Docstring for lib_with_empty_init_1_method_1</p>",
        "arg_string": "",
    },
    {
        "args": '["param_1", "param_2"]',
        "doc": "Docstring for single_class_lib_method_3 with two params",
        "name": "Single Class Lib Method 3",
        "id": 17,
        "synopsis": "Docstring for lib_with_empty_init_1_method_1",
        "html_doc": "<p>Docstring for lib_with_empty_init_1_method_1</p>",
        "arg_string": "",
    },
]

EXPECTED_BUILT_IN_LIBS = {
    Path(robot.libraries.__file__).parent / "BuiltIn.py",
    Path(robot.libraries.__file__).parent / "Collections.py",
    Path(robot.libraries.__file__).parent / "DateTime.py",
    Path(robot.libraries.__file__).parent / "Easter.py",
    Path(robot.libraries.__file__).parent / "OperatingSystem.py",
    Path(robot.libraries.__file__).parent / "Process.py",
    Path(robot.libraries.__file__).parent / "Screenshot.py",
    Path(robot.libraries.__file__).parent / "String.py",
    Path(robot.libraries.__file__).parent / "Telnet.py",
    Path(robot.libraries.__file__).parent / "XML.py",
}
EXPECTED_COLLECTION_WITH_KW_1 = CollectionUpdateWithKeywords(
    EXPECTED_COLLECTION, EXPECTED_COLLECTION_KEYWORDS_1
)
EXPECTED_COLLECTION_WITH_KW_2 = CollectionUpdateWithKeywords(
    EXPECTED_COLLECTION_2, EXPECTED_COLLECTION_KEYWORDS_2
)


class KeywordsImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = FIXTURE_PATH
        self.client = Client("http://localhost:8000", "rfhub", "rfhub")
        self.rfhub_importer = KeywordsImporter(
            self.client, (self.fixture_path,), True, load_mode="insert"
        )

    def test_import_data(self):
        with responses.RequestsMock() as rsps:
            rfhub_importer = KeywordsImporter(
                self.client,
                (self.fixture_path / "LibWithInit",),
                True,
                load_mode="insert",
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
                        "type": "library",
                        "doc_format": "ROBOT",
                        "scope": "test case",
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

    def test_traverse_paths_should_return_set_of_path_on_lib_with_init(self):
        result = self.rfhub_importer._traverse_paths(self.fixture_path / "LibWithInit")
        self.assertEqual(result, EXPECTED_TRAVERSE_PATHS_INIT)

    def test_traverse_paths_should_return_set_of_paths_on_libs_with_empty_init(self):
        result = self.rfhub_importer._traverse_paths(
            self.fixture_path / "LibsWithEmptyInit"
        )
        self.assertEqual(result, EXPECTED_TRAVERSE_PATHS_NO_INIT)

    def test_get_libraries_paths_should_return_set_of_paths(self):
        result = self.rfhub_importer.get_libraries_paths()
        self.assertEqual(result, EXPECTED_GET_LIBRARIES)

    def test_get_libraries_paths_should_return_set_of_paths_on_installed_keywords(self):
        self.rfhub_importer = KeywordsImporter(self.client, tuple(), False, False)
        result = self.rfhub_importer.get_libraries_paths()
        self.assertEqual(result, EXPECTED_BUILT_IN_LIBS)

    def test_get_libraries_paths_should_return_set_of_paths_when_paths_are_tuple(self):
        self.rfhub_importer = KeywordsImporter(
            self.client,
            (
                self.fixture_path / "LibWithInit",
                self.fixture_path / "LibsWithEmptyInit",
            ),
            True,
            False,
        )
        result = self.rfhub_importer.get_libraries_paths()
        self.assertEqual(
            result, EXPECTED_TRAVERSE_PATHS_INIT | EXPECTED_TRAVERSE_PATHS_NO_INIT
        )

    def test__create_collections_should_return_collection_list(self):
        result = self.rfhub_importer.create_collections(
            {
                FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py",
                FIXTURE_PATH / "test_libdoc_file.xml",
            }
        )
        self.assertCountEqual(
            result, [EXPECTED_COLLECTION_WITH_KW_1, EXPECTED_COLLECTION_WITH_KW_2]
        )

    def test_create_collection_should_return_collection(self):
        result = self.rfhub_importer.create_collection(
            FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py"
        )
        self.assertEqual(EXPECTED_COLLECTION_WITH_KW_1, result)

    def test_create_collections_should_return_empty_list_on_data_error(self):
        result = self.rfhub_importer.create_collections(
            {FIXTURE_PATH / "data_error.py"}
        )
        self.assertListEqual([], result)

    def test_create_collections_should_return_empty_list_on_system_exit(self):
        result = self.rfhub_importer.create_collections({FIXTURE_PATH / "arg_parse.py"})
        self.assertListEqual([], result)

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

    def test_is_library_with_init_should_return_true_on_library_with_init(self):
        file = self.fixture_path / "LibWithInit"
        result = self.rfhub_importer._is_library_with_init(file)
        self.assertTrue(
            result, "method should return true if file is python library with init"
        )

    def test_is_library_with_init_should_return_false_on_library_without_init(self):
        file = self.fixture_path / "LibsWithEmptyInit"
        result = self.rfhub_importer._is_library_with_init(file)
        self.assertFalse(
            result, "method should return false if file is python library without init"
        )

    def test_is_robot_keyword_file_should_return_true_on_library(self):
        file = self.fixture_path / "SingleClassLib" / "SingleClassLib.py"
        result = self.rfhub_importer._is_robot_keyword_file(file)
        self.assertTrue(result, "method should return true if file is python library")

    def test_is_robot_keyword_file_should_return_true_on_libdoc(self):
        file = self.fixture_path / "test_libdoc_file.xml"
        result = self.rfhub_importer._is_robot_keyword_file(file)
        self.assertTrue(result, "method should return true if file is libdoc file")

    def test_is_robot_keyword_file_should_return_true_on_resource(self):
        file = self.fixture_path / "test_resource.resource"
        result = self.rfhub_importer._is_robot_keyword_file(file)
        self.assertTrue(result, "method should return true if file is robot resource")

    def test_is_library_file_should_return_false_on_lib_with_init(self):
        file = self.fixture_path / "LibWithInit" / "__init__.py"
        result = KeywordsImporter._is_library_file(file)
        self.assertFalse(result, "method should return true if file is python library")

    def test_is_library_file_should_return_false_on_library_with_init(self):
        file = self.fixture_path / "LibWithInit" / "__init__.py"
        result = KeywordsImporter._is_library_file(file)
        self.assertFalse(
            result, "method should return false if file is python library with init"
        )

    def test_is_libdoc_file_should_return_true_on_libdoc(self):
        file = self.fixture_path / "test_libdoc_file.xml"
        result = KeywordsImporter._is_libdoc_file(file)
        self.assertTrue(result, "method should return true if file is libdoc file")

    def test_is_libdoc_file_should_return_false_on_non_libdoc(self):
        file = self.fixture_path / "not_libdoc_file.xml"
        result = KeywordsImporter._is_libdoc_file(file)
        self.assertFalse(
            result, "method should return false if file is not libdoc file"
        )

    def test_is_libdoc_file_should_return_false_on_non_xml(self):
        file = self.fixture_path / "_private_library.py"
        result = KeywordsImporter._is_libdoc_file(file)
        self.assertFalse(
            result, "method should return false if file is not libdoc file"
        )

    def test_should_ignore_should_return_true_on_deprecated(self):
        file = self.fixture_path / "deprecated_library.py"
        result = KeywordsImporter._should_ignore(file)
        self.assertTrue(
            result, 'method should return true if file starts with "deprecated"'
        )

    def test_should_ignore_should_return_true_on_private(self):
        file = self.fixture_path / "_private_library.py"
        result = KeywordsImporter._should_ignore(file)
        self.assertTrue(result, 'method should return true if file starts with "_"')

    def test_should_ignore_should_return_true_on_excluded(self):
        file = self.fixture_path / "remote.py"
        result = KeywordsImporter._should_ignore(file)
        self.assertTrue(
            result, "method should return true if file in EXCLUDED_LIBRARIES"
        )

    def test_should_ignore_should_return_false_on_library_to_import(self):
        file = self.fixture_path / "SingleClassLib" / "SingleClassLib.py"
        result = KeywordsImporter._should_ignore(file)
        self.assertFalse(
            result, "method should return false if file should be imported"
        )

    def test_is_resource_file_should_return_true(self):
        file = self.fixture_path / "test_resource.resource"
        result = KeywordsImporter._is_resource_file(file)
        self.assertTrue(result, "method should return true if file is resource file")

    def test_is_resource_file_should_return_false(self):
        file = self.fixture_path / "test_file_with_tests.robot"
        result = KeywordsImporter._is_resource_file(file)
        self.assertFalse(
            result, "method should return false if file is not resource file"
        )

    def test_is_resource_file_should_return_false_on_init(self):
        file = self.fixture_path / "__init__.robot"
        result = KeywordsImporter._is_resource_file(file)
        self.assertFalse(
            result, "method should return false if file is not resource file"
        )

    def test_has_keyword_table_should_return_true(self):
        data = "*** Keywords ***"
        result = KeywordsImporter._has_keyword_table(data=data)
        self.assertTrue(result, "method should return true if Keywords were found")

    def test_has_keyword_table_should_return_false(self):
        data = "*** Keys ***"
        result = KeywordsImporter._has_keyword_table(data=data)
        self.assertFalse(
            result, "method should return false if Keywords were not found"
        )

    def test_has_test_case_table_should_return_true(self):
        data = "*** Test Case ***"
        result = KeywordsImporter._has_test_case_table(data=data)
        self.assertTrue(result, "method should return true if Test Case were found")

    def test_has_test_case_table_should_return_false(self):
        data = "*** Test ***"
        result = KeywordsImporter._has_test_case_table(data=data)
        self.assertFalse(
            result, "method should return false if Test Case were not found"
        )

    def test_serialise_libdoc_should_return_collection(self):
        file = self.fixture_path / "test_libdoc_file.xml"
        libdoc_1 = LibraryDocumentation(file)
        serialised_libdoc = self.rfhub_importer._serialise_libdoc(libdoc_1, str(file))
        self.assertEqual(serialised_libdoc, EXPECTED_COLLECTION_2)

    def test_serialise_keywords_should_return_keywords(self):
        file = self.fixture_path / "test_resource.resource"
        libdoc_2 = LibraryDocumentation(file)
        serialised_keywords = self.rfhub_importer._serialise_keywords(libdoc_2)
        self.assertEqual(serialised_keywords, EXPECTED_KEYWORDS)

    def test_extract_doc_from_libdoc_inits_should_return_doc_from_init(self):
        file = str(self.fixture_path / "LibWithInit")
        libdoc = LibraryDocumentation(file)
        init_doc = self.rfhub_importer._extract_doc_from_libdoc_inits(libdoc.inits)
        self.assertEqual(init_doc, EXPECTED_INIT_DOC)

    def test_extract_doc_from_libdoc_inits_should_return_empty_string(self):
        file = str(self.fixture_path / "SingleClassLib" / "SingleClassLib.py")
        libdoc = LibraryDocumentation(file)
        init_doc = self.rfhub_importer._extract_doc_from_libdoc_inits(libdoc.inits)
        self.assertEqual(init_doc, "")

    def test_robot_files_candidates_should_return_true_if_robot_files_present(self):
        self.assertTrue(
            self.rfhub_importer._robot_files_candidates(
                self.fixture_path / "LibWithInit"
            )
        )
        self.assertFalse(
            self.rfhub_importer._robot_files_candidates(
                self.fixture_path / "LibWithEmptyInit"
            )
        )

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
