import responses
import unittest
from pathlib import Path
from robot.libdocpkg import LibraryDocumentation
import robot.libraries

from rfhub2.cli.rfhub_importer import RfhubImporter
from rfhub2.cli.api_client import Client

FIXTURE_PATH = Path.cwd() / 'tests' / 'acceptance' / 'fixtures'
EXPECTED_LIBDOC = {'doc': 'Documentation for library ``Test Libdoc File``.',
                   'doc_format': 'ROBOT', 'name': 'Test Libdoc File',
                   'scope': 'global', 'type': 'library', 'version': '',
                   'keywords': [{'name': 'Someone Shall Pass', 'args': '["who"]', 'doc': ''}]}
EXPECTED_KEYWORDS = [{'args': '', 'doc': 'This keyword was imported from file\n'
                                         'with .resource extension, available since RFWK 3.1',
                      'name': 'Keyword 1 Imported From Resource File'},
                     {'args': '["arg_1", "arg_2"]', 'doc': 'This keyword was imported from file\n'
                                                           'with .resource extension, available since RFWK 3.1',
                      'name': 'Keyword 2 Imported From Resource File'}]
EXPECTED_TRAVERSE_PATHS_INIT = {FIXTURE_PATH / 'LibWithInit'}
EXPECTED_TRAVERSE_PATHS_NO_INIT = {FIXTURE_PATH / 'LibsWithEmptyInit' / 'LibWithEmptyInit1.py',
                                   FIXTURE_PATH / 'LibsWithEmptyInit' / 'LibWithEmptyInit2.py'}
EXPECTED_GET_LIBRARIES = (EXPECTED_TRAVERSE_PATHS_INIT | EXPECTED_TRAVERSE_PATHS_NO_INIT |
                          {FIXTURE_PATH / 'SingleClassLib' / 'SingleClassLib.py',
                           FIXTURE_PATH / 'test_libdoc_file.xml',
                           FIXTURE_PATH / 'test_resource.resource',
                           FIXTURE_PATH / 'test_robot.robot'})
EXPECTED_COLLECTION = {'doc': 'Overview that should be imported for SingleClassLib.',
                       'doc_format': 'ROBOT',
                       'keywords': [{'args': '',
                                     'doc': 'Docstring for single_class_lib_method_1',
                                     'name': 'Single Class Lib Method 1'},
                                    {'args': '',
                                     'doc': 'Docstring for single_class_lib_method_2',
                                     'name': 'Single Class Lib Method 2'},
                                    {'args': '["param_1", "param_2"]',
                                     'doc': 'Docstring for single_class_lib_method_3 with two params',
                                     'name': 'Single Class Lib Method 3'}],
                       'name': 'SingleClassLib',
                       'path': str(FIXTURE_PATH / 'SingleClassLib' / 'SingleClassLib.py'),
                       'scope': 'test case',
                       'type': 'library',
                       'version': ''}
EXPECTED_COLLECTION2 = {'doc': 'Documentation for library ``Test Libdoc File``.',
                        'doc_format': 'ROBOT',
                        'keywords': [{'args': '["who"]', 'doc': '', 'name': 'Someone Shall Pass'}],
                        'name': 'Test Libdoc File',
                        'path': str(FIXTURE_PATH / 'test_libdoc_file.xml'),
                        'scope': 'global',
                        'type': 'library',
                        'version': ''}
EXPECTED_ADD_COLLECTIONS = [{'Test Libdoc File': 1}]

EXPECTED_BUILT_IN_LIBS = {Path(robot.libraries.__file__).parent / 'BuiltIn.py',
                          Path(robot.libraries.__file__).parent / 'Collections.py',
                          Path(robot.libraries.__file__).parent / 'DateTime.py',
                          Path(robot.libraries.__file__).parent / 'Easter.py',
                          Path(robot.libraries.__file__).parent / 'OperatingSystem.py',
                          Path(robot.libraries.__file__).parent / 'Process.py',
                          Path(robot.libraries.__file__).parent / 'Screenshot.py',
                          Path(robot.libraries.__file__).parent / 'String.py',
                          Path(robot.libraries.__file__).parent / 'Telnet.py',
                          Path(robot.libraries.__file__).parent / 'XML.py'}


class RfhubImporterTests(unittest.TestCase):

    def setUp(self) -> None:
        self.fixture_path = FIXTURE_PATH
        self.client = Client('http://localhost:8000', 'rfhub', 'rfhub')
        self.rfhub_importer = RfhubImporter((self.fixture_path, ), True, self.client)

    def test_delete_collections(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.client.api_url}/collections/', json={},
                     status=200, adding_headers={"Content-Type": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/collections/',
                     json={'name': 'healtcheck_collection', 'id': 1},
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.DELETE, f'{self.client.api_url}/collections/1/', status=204,
                     adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.GET, f'{self.client.api_url}/collections/', json=[{'id': 2}, {'id': 66}],
                     status=200, adding_headers={"Content-Type": "application/json"})
            rsps.add(responses.DELETE, f'{self.client.api_url}/collections/2/', status=204,
                     adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.DELETE, f'{self.client.api_url}/collections/66/', status=204,
                     adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            result = self.rfhub_importer.delete_collections()
            self.assertEqual({2, 66}, result)

    def test_import_libraries(self):
        self.rfhub_importer = RfhubImporter((self.fixture_path / 'SingleClassLib',
                                             self.fixture_path / 'LibWithInit'), True, self.client)
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.client.api_url}/collections/', json={},
                     status=200, adding_headers={"Content-Type": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/collections/',
                     json={'name': 'healtcheck_collection', 'id': 1},
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.DELETE, f'{self.client.api_url}/collections/1/', status=204,
                     adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/collections/',
                     json={'name': EXPECTED_COLLECTION['name'], 'id': 1},
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/keywords/', json=EXPECTED_COLLECTION['keywords'][0],
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/collections/',
                     json={'name': 'LibWithInit', 'id': 2},
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/keywords/', json=EXPECTED_COLLECTION['keywords'][0],
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            result = self.rfhub_importer.import_libraries()
            self.assertCountEqual(result, (2, 7))

    def test_traverse_paths_should_return_set_of_path_on_lib_with_init(self):
        result = self.rfhub_importer._traverse_paths(self.fixture_path / 'LibWithInit')
        self.assertEqual(result, EXPECTED_TRAVERSE_PATHS_INIT)

    def test_traverse_paths_should_return_set_of_paths_on_libs_with_empty_init(self):
        result = self.rfhub_importer._traverse_paths(self.fixture_path / 'LibsWithEmptyInit')
        self.assertEqual(result, EXPECTED_TRAVERSE_PATHS_NO_INIT)

    def test_get_libraries_paths_should_return_set_of_paths(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.client.api_url}/collections/', json={},
                     status=200, adding_headers={"Content-Type": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/collections/', json={'name': 'healtcheck_collection', 'id': 1},
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.DELETE, f'{self.client.api_url}/collections/1/', status=204,
                     adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            result = self.rfhub_importer.get_libraries_paths()
            self.assertEqual(result, EXPECTED_GET_LIBRARIES)

    def test_get_libraries_paths_should_return_set_of_paths_on_installed_keywords(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.client.api_url}/collections/', json={},
                     status=200, adding_headers={"Content-Type": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/collections/', json={'name': 'healtcheck_collection', 'id': 1},
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.DELETE, f'{self.client.api_url}/collections/1/', status=204,
                     adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            self.rfhub_importer = RfhubImporter(tuple(), False, self.client)
            result = self.rfhub_importer.get_libraries_paths()
            self.assertEqual(result, EXPECTED_BUILT_IN_LIBS)

    def test_get_libraries_paths_should_return_set_of_paths_when_paths_are_tuple(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{self.client.api_url}/collections/', json={},
                     status=200, adding_headers={"Content-Type": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/collections/', json={'name': 'healtcheck_collection', 'id': 1},
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.DELETE, f'{self.client.api_url}/collections/1/', status=204,
                     adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            self.rfhub_importer = RfhubImporter((self.fixture_path / 'LibWithInit',
                                                 self.fixture_path / 'LibsWithEmptyInit'), True, self.client)
            result = self.rfhub_importer.get_libraries_paths()
            self.assertEqual(result, EXPECTED_TRAVERSE_PATHS_INIT | EXPECTED_TRAVERSE_PATHS_NO_INIT)

    def test__create_collections_should_return_collection_list(self):
        result = self.rfhub_importer.create_collections({FIXTURE_PATH / 'SingleClassLib' / 'SingleClassLib.py',
                                                        FIXTURE_PATH / 'test_libdoc_file.xml'})
        self.assertCountEqual(result, [EXPECTED_COLLECTION, EXPECTED_COLLECTION2])

    def test_create_collection_should_return_collection(self):
        result = self.rfhub_importer.create_collection(FIXTURE_PATH / 'SingleClassLib' / 'SingleClassLib.py')
        self.assertDictEqual(EXPECTED_COLLECTION, result)

    def test_add_collections_should_return_loaded_collections_and_keywords_number(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{self.client.api_url}/collections/',
                     json={'name': EXPECTED_COLLECTION2['name'], 'id': 1},
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            rsps.add(responses.POST, f'{self.client.api_url}/keywords/', json=EXPECTED_COLLECTION2['keywords'][0],
                     status=201, adding_headers={"Content-Type": "application/json", "accept": "application/json"})
            result = self.rfhub_importer.add_collections([EXPECTED_COLLECTION2])
            self.assertCountEqual(result, EXPECTED_ADD_COLLECTIONS)

    def test_is_library_with_init_should_return_true_on_library_with_init(self):
        file = self.fixture_path / 'LibWithInit'
        result = self.rfhub_importer._is_library_with_init(file)
        self.assertTrue(result, 'method should return true if file is python library with init')

    def test_is_library_with_init_should_return_false_on_library_without_init(self):
        file = self.fixture_path / 'LibsWithEmptyInit'
        result = self.rfhub_importer._is_library_with_init(file)
        self.assertFalse(result, 'method should return false if file is python library without init')

    def test_is_robot_keyword_file_should_return_true_on_library(self):
        file = self.fixture_path / 'SingleClassLib' / 'SingleClassLib.py'
        result = self.rfhub_importer._is_robot_keyword_file(file)
        self.assertTrue(result, 'method should return true if file is python library')

    def test_is_robot_keyword_file_should_return_true_on_libdoc(self):
        file = self.fixture_path / 'test_libdoc_file.xml'
        result = self.rfhub_importer._is_robot_keyword_file(file)
        self.assertTrue(result, 'method should return true if file is libdoc file')

    def test_is_robot_keyword_file_should_return_true_on_resource(self):
        file = self.fixture_path / 'test_resource.resource'
        result = self.rfhub_importer._is_robot_keyword_file(file)
        self.assertTrue(result, 'method should return true if file is robot resource')

    def test_is_library_file_should_return_false_on_lib_with_init(self):
        file = self.fixture_path / 'LibWithInit' / '__init__.py'
        result = RfhubImporter._is_library_file(file)
        self.assertFalse(result, 'method should return true if file is python library')

    def test_is_library_file_should_return_false_on_library_with_init(self):
        file = self.fixture_path / 'LibWithInit' / '__init__.py'
        result = RfhubImporter._is_library_file(file)
        self.assertFalse(result, 'method should return false if file is python library with init')

    def test_is_libdoc_file_should_return_true_on_libdoc(self):
        file = self.fixture_path / 'test_libdoc_file.xml'
        result = RfhubImporter._is_libdoc_file(file)
        self.assertTrue(result, 'method should return true if file is libdoc file')

    def test_is_libdoc_file_should_return_false_on_non_libdoc(self):
        file = self.fixture_path / 'not_libdoc_file.xml'
        result = RfhubImporter._is_libdoc_file(file)
        self.assertFalse(result, 'method should return false if file is not libdoc file')

    def test_is_libdoc_file_should_return_false_on_non_xml(self):
        file = self.fixture_path / '_private_library.py'
        result = RfhubImporter._is_libdoc_file(file)
        self.assertFalse(result, 'method should return false if file is not libdoc file')

    def test_should_ignore_should_return_true_on_deprecated(self):
        file = self.fixture_path / 'deprecated_library.py'
        result = RfhubImporter._should_ignore(file)
        self.assertTrue(result, 'method should return true if file starts with \"deprecated\"')

    def test_should_ignore_should_return_true_on_private(self):
        file = self.fixture_path / '_private_library.py'
        result = RfhubImporter._should_ignore(file)
        self.assertTrue(result, 'method should return true if file starts with \"_\"')

    def test_should_ignore_should_return_true_on_excluded(self):
        file = self.fixture_path / 'remote.py'
        result = RfhubImporter._should_ignore(file)
        self.assertTrue(result, 'method should return true if file in EXCLUDED_LIBRARIES')

    def test_should_ignore_should_return_false_on_library_to_import(self):
        file = self.fixture_path / 'SingleClassLib' / 'SingleClassLib.py'
        result = RfhubImporter._should_ignore(file)
        self.assertFalse(result, 'method should return false if file should be imported')

    def test_is_resource_file_should_return_true(self):
        file = self.fixture_path / 'test_resource.resource'
        result = RfhubImporter._is_resource_file(file)
        self.assertTrue(result, 'method should return true if file is resource file')

    def test_is_resource_file_should_return_false(self):
        file = self.fixture_path / 'test_file_with_tests.robot'
        result = RfhubImporter._is_resource_file(file)
        self.assertFalse(result, 'method should return false if file is not resource file')

    def test_is_resource_file_should_return_false_on_init(self):
        file = self.fixture_path / '__init__.robot'
        result = RfhubImporter._is_resource_file(file)
        self.assertFalse(result, 'method should return false if file is not resource file')

    def test_has_keyword_table_should_return_true(self):
        data = '*** Keywords ***'
        result = RfhubImporter._has_keyword_table(data=data)
        self.assertTrue(result, 'method should return true if Keywords were found')

    def test_has_keyword_table_should_return_false(self):
        data = '*** Keys ***'
        result = RfhubImporter._has_keyword_table(data=data)
        self.assertFalse(result, 'method should return false if Keywords were not found')

    def test_has_test_case_table_should_return_true(self):
        data = '*** Test Case ***'
        result = RfhubImporter._has_test_case_table(data=data)
        self.assertTrue(result, 'method should return true if Test Case were found')

    def test_has_test_case_table_should_return_false(self):
        data = '*** Test ***'
        result = RfhubImporter._has_test_case_table(data=data)
        self.assertFalse(result, 'method should return false if Test Case were not found')

    def test_serialise_libdoc_should_return_collection(self):
        file = self.fixture_path / 'test_libdoc_file.xml'
        libdoc = LibraryDocumentation(file)
        serialised_keywords = self.rfhub_importer._serialise_keywords(libdoc)
        serialised_libdoc = self.rfhub_importer._serialise_libdoc(libdoc, file, serialised_keywords)
        serialised_libdoc.pop('path')
        self.assertEqual(serialised_libdoc, EXPECTED_LIBDOC)

    def test_serialise_keywords_should_return_keywords(self):
        file = self.fixture_path / 'test_resource.resource'
        libdoc = LibraryDocumentation(file)
        serialised_keywords = self.rfhub_importer._serialise_keywords(libdoc)
        self.assertEqual(serialised_keywords, EXPECTED_KEYWORDS)
