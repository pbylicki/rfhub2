import copy
import responses
import unittest
from pathlib import Path
from robot.libdocpkg import LibraryDocumentation
import robot.libraries

from rfhub2.cli.rfhub_importer import RfhubImporter
from rfhub2.cli.api_client import Client

FIXTURE_PATH = Path.cwd() / "tests" / "fixtures" / "initial"
EXPECTED_LIBDOC = {
    "doc": "Documentation for library ``Test Libdoc File``.",
    "doc_format": "ROBOT",
    "name": "Test Libdoc File",
    "scope": "global",
    "type": "library",
    "version": "3.2.0",
    "keywords": [{"name": "Someone Shall Pass", "args": '["who"]', "doc": ""}],
}
EXPECTED_KEYWORDS = [
    {
        "args": "",
        "doc": "This keyword was imported from file\n"
        "with .resource extension, available since RFWK 3.1",
        "name": "Keyword 1 Imported From Resource File",
    },
    {
        "args": '["arg_1", "arg_2"]',
        "doc": "This keyword was imported from file\n"
        "with .resource extension, available since RFWK 3.1",
        "name": "Keyword 2 Imported From Resource File",
    },
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
    }
)
EXPECTED_COLLECTION = {
    "doc": "Overview that should be imported for SingleClassLib.",
    "doc_format": "ROBOT",
    "keywords": [
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
    ],
    "name": "SingleClassLib",
    "path": str(FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py"),
    "scope": "test case",
    "type": "library",
    "version": "1.2.3",
}
EXPECTED_COLLECTION2 = {
    "doc": "Documentation for library ``Test Libdoc File``.",
    "doc_format": "ROBOT",
    "keywords": [{"args": '["who"]', "doc": "", "name": "Someone Shall Pass"}],
    "name": "Test Libdoc File",
    "path": str(FIXTURE_PATH / "test_libdoc_file.xml"),
    "scope": "global",
    "type": "library",
    "version": "3.2.0",
}
EXPECTED_ADD_COLLECTIONS = [{"name": "Test Libdoc File", "keywords": 1}]
EXPECTED_UPDATE_COLLECTIONS = [
    {"name": "a", "keywords": 3},
    {"name": "b", "keywords": 3},
    {"name": "c", "keywords": 3},
    {"name": "e", "keywords": 3},
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


class RfhubImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = FIXTURE_PATH
        self.client = Client("http://localhost:8000", "rfhub", "rfhub")
        self.rfhub_importer = RfhubImporter(
            self.client, (self.fixture_path,), True, mode="insert"
        )

    def test_import_libraries_insert_mode(self):
        with responses.RequestsMock() as rsps:
            rfhub_importer = RfhubImporter(
                self.client, (self.fixture_path / "LibWithInit",), True, mode="insert"
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
            rfhub_importer = RfhubImporter(
                self.client, (self.fixture_path / "LibWithInit",), True, mode="append"
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
            rfhub_importer = RfhubImporter(
                self.client, (self.fixture_path / "LibWithInit",), True, mode="update"
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
            for i in (0, 100):
                rsps.add(
                    responses.GET,
                    f"{self.client.api_url}/collections/?skip={i}&limit=100",
                    json=[{"id": i}],
                    status=200,
                    adding_headers={"Content-Type": "application/json"},
                )
            rsps.add(
                responses.GET,
                f"{self.client.api_url}/collections/?skip=200&limit=100",
                json=[],
                status=200,
                adding_headers={"Content-Type": "application/json"},
            )
            result = self.rfhub_importer.get_all_collections()
            self.assertListEqual([{"id": 0}, {"id": 100}], result)

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
        self.rfhub_importer = RfhubImporter(self.client, tuple(), False, False)
        result = self.rfhub_importer.get_libraries_paths()
        self.assertEqual(result, EXPECTED_BUILT_IN_LIBS)

    def test_get_libraries_paths_should_return_set_of_paths_when_paths_are_tuple(self):
        self.rfhub_importer = RfhubImporter(
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
        self.assertCountEqual(result, [EXPECTED_COLLECTION, EXPECTED_COLLECTION2])

    def test_create_collection_should_return_collection(self):
        result = self.rfhub_importer.create_collection(
            FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py"
        )
        self.assertDictEqual(EXPECTED_COLLECTION, result)

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
            {
                "id": 1,
                "path": "1",
                "type": "library",
                "version": "1",
                "name": "a",
                "keywords": KEYWORDS_EXTENDED,
            },
            {
                "id": 2,
                "path": "2",
                "type": "library",
                "version": "2",
                "name": "b",
                "keywords": KEYWORDS_EXTENDED,
            },
            {
                "id": 3,
                "path": "3",
                "type": "library",
                "version": "3",
                "name": "c",
                "keywords": KEYWORDS_EXTENDED,
            },
            {
                "id": 4,
                "path": "4",
                "type": "resource",
                "version": "",
                "name": "d",
                "keywords": KEYWORDS_EXTENDED,
            },
            {
                "id": 5,
                "path": "5",
                "type": "resource",
                "version": "",
                "name": "e",
                "keywords": KEYWORDS_2,
            },
        ]

        new_collections = [
            {
                "id": 1,
                "path": "1",
                "type": "library",
                "version": "2",
                "name": "a",
                "keywords": KEYWORDS_1,
            },
            {
                "id": 2,
                "path": "2",
                "type": "library",
                "version": "3",
                "name": "b",
                "keywords": KEYWORDS_1,
            },
            {
                "id": 3,
                "path": "3",
                "type": "library",
                "version": "4",
                "name": "c",
                "keywords": KEYWORDS_1,
            },
            {
                "id": 4,
                "path": "4",
                "type": "resource",
                "version": "",
                "name": "d",
                "keywords": KEYWORDS_1,
            },
            {
                "id": 5,
                "path": "5",
                "type": "resource",
                "version": "",
                "name": "e",
                "keywords": KEYWORDS_1,
            },
        ]
        with responses.RequestsMock() as rsps:
            for i in range(1, 5):
                rsps.add(
                    responses.POST,
                    f"{self.client.api_url}/collections/",
                    json=new_collections[0],
                    status=201,
                    adding_headers={
                        "Content-Type": "application/json",
                        "accept": "application/json",
                    },
                )
                for j in range(1, 4):
                    rsps.add(
                        responses.POST,
                        f"{self.client.api_url}/keywords/",
                        json=new_collections[0]["keywords"][0],
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
            {
                "id": 1,
                "path": "1",
                "type": "library",
                "version": "1",
                "name": "a",
                "keywords": [],
            },
            {
                "id": 2,
                "path": "2",
                "type": "library",
                "version": "2",
                "name": "b",
                "keywords": [],
            },
            {
                "id": 3,
                "path": "3",
                "type": "library",
                "version": "3",
                "name": "c",
                "keywords": [],
            },
        ]

        new_collections = [
            {
                "id": 1,
                "path": "1",
                "type": "library",
                "version": "2",
                "name": "a",
                "keywords": [],
            },
            {
                "id": 2,
                "path": "2",
                "type": "library",
                "version": "3",
                "name": "b",
                "keywords": [],
            },
            {
                "id": 3,
                "path": "3",
                "type": "library",
                "version": "4",
                "name": "c",
                "keywords": [],
            },
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
                json={"name": EXPECTED_COLLECTION2["name"], "id": 1},
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            rsps.add(
                responses.POST,
                f"{self.client.api_url}/keywords/",
                json=EXPECTED_COLLECTION2["keywords"][0],
                status=201,
                adding_headers={
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
            result = self.rfhub_importer.add_collections([EXPECTED_COLLECTION2])
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
                self.rfhub_importer.add_collections([EXPECTED_COLLECTION2])

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
        result = RfhubImporter._is_library_file(file)
        self.assertFalse(result, "method should return true if file is python library")

    def test_is_library_file_should_return_false_on_library_with_init(self):
        file = self.fixture_path / "LibWithInit" / "__init__.py"
        result = RfhubImporter._is_library_file(file)
        self.assertFalse(
            result, "method should return false if file is python library with init"
        )

    def test_is_libdoc_file_should_return_true_on_libdoc(self):
        file = self.fixture_path / "test_libdoc_file.xml"
        result = RfhubImporter._is_libdoc_file(file)
        self.assertTrue(result, "method should return true if file is libdoc file")

    def test_is_libdoc_file_should_return_false_on_non_libdoc(self):
        file = self.fixture_path / "not_libdoc_file.xml"
        result = RfhubImporter._is_libdoc_file(file)
        self.assertFalse(
            result, "method should return false if file is not libdoc file"
        )

    def test_is_libdoc_file_should_return_false_on_non_xml(self):
        file = self.fixture_path / "_private_library.py"
        result = RfhubImporter._is_libdoc_file(file)
        self.assertFalse(
            result, "method should return false if file is not libdoc file"
        )

    def test_should_ignore_should_return_true_on_deprecated(self):
        file = self.fixture_path / "deprecated_library.py"
        result = RfhubImporter._should_ignore(file)
        self.assertTrue(
            result, 'method should return true if file starts with "deprecated"'
        )

    def test_should_ignore_should_return_true_on_private(self):
        file = self.fixture_path / "_private_library.py"
        result = RfhubImporter._should_ignore(file)
        self.assertTrue(result, 'method should return true if file starts with "_"')

    def test_should_ignore_should_return_true_on_excluded(self):
        file = self.fixture_path / "remote.py"
        result = RfhubImporter._should_ignore(file)
        self.assertTrue(
            result, "method should return true if file in EXCLUDED_LIBRARIES"
        )

    def test_should_ignore_should_return_false_on_library_to_import(self):
        file = self.fixture_path / "SingleClassLib" / "SingleClassLib.py"
        result = RfhubImporter._should_ignore(file)
        self.assertFalse(
            result, "method should return false if file should be imported"
        )

    def test_is_resource_file_should_return_true(self):
        file = self.fixture_path / "test_resource.resource"
        result = RfhubImporter._is_resource_file(file)
        self.assertTrue(result, "method should return true if file is resource file")

    def test_is_resource_file_should_return_false(self):
        file = self.fixture_path / "test_file_with_tests.robot"
        result = RfhubImporter._is_resource_file(file)
        self.assertFalse(
            result, "method should return false if file is not resource file"
        )

    def test_is_resource_file_should_return_false_on_init(self):
        file = self.fixture_path / "__init__.robot"
        result = RfhubImporter._is_resource_file(file)
        self.assertFalse(
            result, "method should return false if file is not resource file"
        )

    def test_has_keyword_table_should_return_true(self):
        data = "*** Keywords ***"
        result = RfhubImporter._has_keyword_table(data=data)
        self.assertTrue(result, "method should return true if Keywords were found")

    def test_has_keyword_table_should_return_false(self):
        data = "*** Keys ***"
        result = RfhubImporter._has_keyword_table(data=data)
        self.assertFalse(
            result, "method should return false if Keywords were not found"
        )

    def test_has_test_case_table_should_return_true(self):
        data = "*** Test Case ***"
        result = RfhubImporter._has_test_case_table(data=data)
        self.assertTrue(result, "method should return true if Test Case were found")

    def test_has_test_case_table_should_return_false(self):
        data = "*** Test ***"
        result = RfhubImporter._has_test_case_table(data=data)
        self.assertFalse(
            result, "method should return false if Test Case were not found"
        )

    def test_serialise_libdoc_should_return_collection(self):
        file = self.fixture_path / "test_libdoc_file.xml"
        libdoc = LibraryDocumentation(file)
        serialised_keywords = self.rfhub_importer._serialise_keywords(libdoc)
        serialised_libdoc = self.rfhub_importer._serialise_libdoc(
            libdoc, file, serialised_keywords
        )
        serialised_libdoc.pop("path")
        self.assertEqual(serialised_libdoc, EXPECTED_LIBDOC)

    def test_serialise_keywords_should_return_keywords(self):
        file = self.fixture_path / "test_resource.resource"
        libdoc = LibraryDocumentation(file)
        serialised_keywords = self.rfhub_importer._serialise_keywords(libdoc)
        self.assertEqual(serialised_keywords, EXPECTED_KEYWORDS)

    def test_collection_path_and_name_match_should_return_true_when_matched(self):
        result = RfhubImporter._collection_path_and_name_match(
            EXPECTED_COLLECTION, EXPECTED_COLLECTION
        )
        self.assertTrue(result)

    def test_collection_path_and_name_match_should_return_false_when_not_matched(self):
        result = RfhubImporter._collection_path_and_name_match(
            EXPECTED_COLLECTION, EXPECTED_COLLECTION2
        )
        self.assertFalse(result)

    def test_get_collections_to_update_should_return_collections_to_update(self):
        existing_collections = [EXPECTED_COLLECTION, EXPECTED_COLLECTION2]
        new_collections = copy.deepcopy(existing_collections)
        new_collections[0]["version"] = "1.2.4"
        new_collections[1]["version"] = "3.3.0"
        result = RfhubImporter._get_collections_to_update(
            existing_collections, new_collections
        )
        self.assertListEqual(new_collections, result)

    def test_get_new_collections_should_return_only_new_collections(self):
        exisitng_collections = [EXPECTED_COLLECTION]
        new_collections = [EXPECTED_COLLECTION, EXPECTED_COLLECTION2]
        result = RfhubImporter._get_new_collections(
            exisitng_collections, new_collections
        )
        self.assertListEqual([EXPECTED_COLLECTION2], result)

    def test_reduce_collection_items_should_return_reduced_collection(self):
        collection2 = copy.deepcopy(EXPECTED_COLLECTION)
        EXPECTED_COLLECTION["id"] = 1
        EXPECTED_COLLECTION["keywords"] = KEYWORDS_EXTENDED
        result = RfhubImporter._reduce_collection_items(
            collection2, EXPECTED_COLLECTION
        )
        self.assertDictEqual(collection2, result)

    def test_get_reduced_collection_should_return_reduced_collection(self):
        collection2 = copy.deepcopy(EXPECTED_COLLECTION2)
        collection2["id"] = 1
        result = RfhubImporter._get_reduced_collection(
            EXPECTED_COLLECTION2, collection2
        )
        self.assertDictEqual(EXPECTED_COLLECTION2, result)

    def test_get_reduced_keywords_should_return_reduced_keywords(self):
        result = RfhubImporter._get_reduced_keywords(KEYWORDS_1, KEYWORDS_EXTENDED)
        self.assertListEqual(KEYWORDS_1, result)

    def test_library_or_resource_changed_should_return_false_when_library_unchanged(
        self
    ):
        result = RfhubImporter._library_or_resource_changed(
            EXPECTED_COLLECTION, EXPECTED_COLLECTION
        )
        self.assertFalse(result)

    def test_library_or_resource_changed_should_return_true_when_library_changed(self):
        collection2 = copy.deepcopy(EXPECTED_COLLECTION)
        collection2["version"] = "1.2.4"
        result = RfhubImporter._library_or_resource_changed(
            EXPECTED_COLLECTION, collection2
        )
        self.assertTrue(result)

    def test_library_or_resource_changed_should_return_true_when_resource_unchanged(
        self
    ):
        EXPECTED_COLLECTION["type"] = "resource"
        collection2 = copy.deepcopy(EXPECTED_COLLECTION)
        result = RfhubImporter._library_or_resource_changed(
            EXPECTED_COLLECTION, collection2
        )
        self.assertFalse(result)

    def test_library_or_resource_changed_should_return_true_when_resource_changed(self):
        EXPECTED_COLLECTION["type"] = "resource"
        collection2 = copy.deepcopy(EXPECTED_COLLECTION)
        collection2["doc"] = "abc"
        result = RfhubImporter._library_or_resource_changed(
            EXPECTED_COLLECTION, collection2
        )
        self.assertTrue(result)
