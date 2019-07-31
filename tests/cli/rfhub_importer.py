import unittest
from pathlib import Path
from robot.libdocpkg import LibraryDocumentation

from rfhub2.cli.rfhub_importer import RfhubImporter
from rfhub2.cli.api_client import Client

EXPECTED_LIBDOC = {'doc': 'Documentation for library ``Test Libdoc File``.',
                   'doc_format': 'ROBOT', 'name': 'Test Libdoc File',
                   'scope': 'global', 'type': 'library', 'version': ''}
EXPECTED_KEYWORDS = [{'args': '', 'doc': 'This keyword was imported from file\n'
                                         'with .resource extension, available since RFWK 3.1',
                      'name': 'Keyword 1 Imported From Resource File'},
                     {'args': '["arg_1", "arg_2"]', 'doc': 'This keyword was imported from file\n'
                                                           'with .resource extension, available since RFWK 3.1',
                      'name': 'Keyword 2 Imported From Resource File'}]


class RfhubImporterTests(unittest.TestCase):

    def setUp(self) -> None:
        self.fixture_path = Path.cwd() / 'tests' / 'acceptance' / 'fixtures'
        self.client = Client('http//localhost:8000', 'rfhub', 'rfhub')
        self.rfhub_importer = RfhubImporter(self.fixture_path, False, self.client)

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
        serialised_libdoc = self.rfhub_importer._serialise_libdoc(libdoc, file)
        serialised_libdoc.pop('path')
        self.assertEqual(serialised_libdoc, EXPECTED_LIBDOC)

    def test_serialise_keywords_should_return_keywords(self):
        file = self.fixture_path / 'test_resource.resource'
        libdoc = LibraryDocumentation(file)
        serialised_keywords = self.rfhub_importer._serialise_keywords(libdoc)
        self.assertEqual(serialised_keywords, EXPECTED_KEYWORDS)
