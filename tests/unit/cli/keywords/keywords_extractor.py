from importlib.util import find_spec
from robot.libdocpkg import LibraryDocumentation
import unittest

from rfhub2.cli.keywords.keywords_extractor import KeywordsExtractor
from .test_data import *


class KeywordsExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = FIXTURE_PATH
        self.rfhub_extractor = KeywordsExtractor((self.fixture_path,), True, "", "")

    def test_traverse_paths_should_return_set_of_path_on_lib_with_init(self):
        result = self.rfhub_extractor._traverse_paths(self.fixture_path / "LibWithInit")
        self.assertEqual(result, EXPECTED_TRAVERSE_PATHS_INIT)

    def test_traverse_paths_should_return_set_of_paths_on_libs_with_empty_init(self):
        result = self.rfhub_extractor._traverse_paths(
            self.fixture_path / "LibsWithEmptyInit"
        )
        self.assertEqual(result, EXPECTED_TRAVERSE_PATHS_NO_INIT)

    def test_get_libraries_paths_should_return_set_of_paths(self):
        result = self.rfhub_extractor.get_libraries_paths()
        self.assertEqual(result, EXPECTED_GET_LIBRARIES)

    def test_get_library_path_from_name_should_return_path(self):
        requests_path = find_spec("RequestsLibrary").submodule_search_locations[0]
        results = [
            self.rfhub_extractor.get_library_path_from_name(path)
            for path in (self.fixture_path, "RequestsLibrary", "Noffin")
        ]
        self.assertListEqual(results, [str(self.fixture_path), requests_path, None])

    def test_get_libraries_paths_should_return_set_of_paths_on_installed_keywords(self):
        self.rfhub_extractor = KeywordsExtractor(tuple(), False, "", "")
        result = self.rfhub_extractor.get_libraries_paths()
        self.assertEqual(result, EXPECTED_BUILT_IN_LIBS)

    def test_get_libraries_paths_should_return_set_of_paths_when_paths_are_tuple(self):
        self.rfhub_extractor = KeywordsExtractor(
            (
                self.fixture_path / "LibWithInit",
                self.fixture_path / "LibsWithEmptyInit",
            ),
            True,
            "",
            "",
        )
        result = self.rfhub_extractor.get_libraries_paths()
        self.assertEqual(
            result, EXPECTED_TRAVERSE_PATHS_INIT | EXPECTED_TRAVERSE_PATHS_NO_INIT
        )

    def test__create_collections_should_return_collection_list(self):
        result = self.rfhub_extractor.create_collections(
            {
                FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py",
                FIXTURE_PATH / "test_libdoc_file.xml",
            }
        )
        self.assertCountEqual(
            result, [EXPECTED_COLLECTION_WITH_KW_1, EXPECTED_COLLECTION_WITH_KW_2]
        )

    def test_create_collection_should_return_collection(self):
        result = self.rfhub_extractor.create_collection(
            FIXTURE_PATH / "SingleClassLib" / "SingleClassLib.py"
        )
        self.assertEqual(EXPECTED_COLLECTION_WITH_KW_1, result)

    def test_create_collections_should_return_empty_list_on_data_error(self):
        result = self.rfhub_extractor.create_collections(
            {FIXTURE_PATH / "data_error.py"}
        )
        self.assertListEqual([], result)

    def test_create_collections_should_return_empty_list_on_system_exit(self):
        result = self.rfhub_extractor.create_collections(
            {FIXTURE_PATH / "arg_parse.py"}
        )
        self.assertListEqual([], result)

    def test_is_library_with_init_should_return_true_on_library_with_init(self):
        file = self.fixture_path / "LibWithInit"
        result = self.rfhub_extractor._is_library_with_init(file)
        self.assertTrue(
            result, "method should return true if file is python library with init"
        )

    def test_is_library_with_init_should_return_false_on_library_without_init(self):
        file = self.fixture_path / "LibsWithEmptyInit"
        result = self.rfhub_extractor._is_library_with_init(file)
        self.assertFalse(
            result, "method should return false if file is python library without init"
        )

    def test_is_robot_keyword_file_should_return_true_on_library(self):
        file = self.fixture_path / "SingleClassLib" / "SingleClassLib.py"
        result = self.rfhub_extractor._is_robot_keyword_file(file)
        self.assertTrue(result, "method should return true if file is python library")

    def test_is_robot_keyword_file_should_return_true_on_libdoc(self):
        file = self.fixture_path / "test_libdoc_file.xml"
        result = self.rfhub_extractor._is_robot_keyword_file(file)
        self.assertTrue(result, "method should return true if file is libdoc file")

    def test_is_robot_keyword_file_should_return_true_on_resource(self):
        file = self.fixture_path / "test_resource.resource"
        result = self.rfhub_extractor._is_robot_keyword_file(file)
        self.assertTrue(result, "method should return true if file is robot resource")

    def test_is_library_file_should_return_false_on_lib_with_init(self):
        file = self.fixture_path / "LibWithInit" / "__init__.py"
        result = KeywordsExtractor._is_library_file(file)
        self.assertFalse(result, "method should return true if file is python library")

    def test_is_library_file_should_return_false_on_library_with_init(self):
        file = self.fixture_path / "LibWithInit" / "__init__.py"
        result = KeywordsExtractor._is_library_file(file)
        self.assertFalse(
            result, "method should return false if file is python library with init"
        )

    def test_is_libdoc_file_should_return_true_on_libdoc(self):
        file = self.fixture_path / "test_libdoc_file.xml"
        result = KeywordsExtractor._is_libdoc_file(file)
        self.assertTrue(result, "method should return true if file is libdoc file")

    def test_is_libdoc_file_should_return_false_on_non_libdoc(self):
        file = self.fixture_path / "not_libdoc_file.xml"
        result = KeywordsExtractor._is_libdoc_file(file)
        self.assertFalse(
            result, "method should return false if file is not libdoc file"
        )

    def test_is_libdoc_file_should_return_false_on_non_xml(self):
        file = self.fixture_path / "_private_library.py"
        result = KeywordsExtractor._is_libdoc_file(file)
        self.assertFalse(
            result, "method should return false if file is not libdoc file"
        )

    def test_should_ignore_should_return_true_on_deprecated(self):
        file = self.fixture_path / "deprecated_library.py"
        result = KeywordsExtractor._should_ignore(file)
        self.assertTrue(
            result, 'method should return true if file starts with "deprecated"'
        )

    def test_should_ignore_should_return_true_on_private(self):
        file = self.fixture_path / "_private_library.py"
        result = KeywordsExtractor._should_ignore(file)
        self.assertTrue(result, 'method should return true if file starts with "_"')

    def test_should_ignore_should_return_true_on_excluded(self):
        file = self.fixture_path / "remote.py"
        result = KeywordsExtractor._should_ignore(file)
        self.assertTrue(
            result, "method should return true if file in EXCLUDED_LIBRARIES"
        )

    def test_should_ignore_should_return_false_on_library_to_import(self):
        file = self.fixture_path / "SingleClassLib" / "SingleClassLib.py"
        result = KeywordsExtractor._should_ignore(file)
        self.assertFalse(
            result, "method should return false if file should be imported"
        )

    def test_is_resource_file_should_return_true(self):
        file = self.fixture_path / "test_resource.resource"
        result = KeywordsExtractor._is_resource_file(file)
        self.assertTrue(result, "method should return true if file is resource file")

    def test_is_resource_file_should_return_false(self):
        file = self.fixture_path / "test_file_with_tests.robot"
        result = KeywordsExtractor._is_resource_file(file)
        self.assertFalse(
            result, "method should return false if file is not resource file"
        )

    def test_is_resource_file_should_return_false_on_init(self):
        file = self.fixture_path / "__init__.robot"
        result = KeywordsExtractor._is_resource_file(file)
        self.assertFalse(
            result, "method should return false if file is not resource file"
        )

    def test_has_keyword_table_should_return_true(self):
        data = "*** Keywords ***"
        result = KeywordsExtractor._has_keyword_table(data=data)
        self.assertTrue(result, "method should return true if Keywords were found")

    def test_has_keyword_table_should_return_false(self):
        data = "*** Keys ***"
        result = KeywordsExtractor._has_keyword_table(data=data)
        self.assertFalse(
            result, "method should return false if Keywords were not found"
        )

    def test_has_test_case_table_should_return_true(self):
        data = "*** Test Case ***"
        result = KeywordsExtractor._has_test_case_table(data=data)
        self.assertTrue(result, "method should return true if Test Case were found")

    def test_has_test_case_table_should_return_false(self):
        data = "*** Test ***"
        result = KeywordsExtractor._has_test_case_table(data=data)
        self.assertFalse(
            result, "method should return false if Test Case were not found"
        )

    def test_serialise_libdoc_should_return_collection(self):
        file = self.fixture_path / "test_libdoc_file.xml"
        libdoc_1 = LibraryDocumentation(file)
        serialised_libdoc = self.rfhub_extractor._serialise_libdoc(libdoc_1, str(file))
        self.assertEqual(serialised_libdoc, EXPECTED_COLLECTION_2)

    def test_serialise_keywords_should_return_keywords(self):
        file = self.fixture_path / "test_resource.resource"
        libdoc_2 = LibraryDocumentation(file)
        serialised_keywords = self.rfhub_extractor._serialise_keywords(libdoc_2)
        self.assertEqual(serialised_keywords, EXPECTED_KEYWORDS)

    def test_extract_doc_from_libdoc_inits_should_return_doc_from_init(self):
        file = str(self.fixture_path / "LibWithInit")
        libdoc = LibraryDocumentation(file)
        init_doc = self.rfhub_extractor._extract_doc_from_libdoc_inits(libdoc.inits)
        self.assertEqual(init_doc, EXPECTED_INIT_DOC)

    def test_extract_doc_from_libdoc_inits_should_return_empty_string(self):
        file = str(self.fixture_path / "SingleClassLib" / "SingleClassLib.py")
        libdoc = LibraryDocumentation(file)
        init_doc = self.rfhub_extractor._extract_doc_from_libdoc_inits(libdoc.inits)
        self.assertEqual(init_doc, "")

    def test_robot_files_candidates_should_return_true_if_robot_files_present(self):
        self.assertTrue(
            self.rfhub_extractor._robot_files_candidates(
                self.fixture_path / "LibWithInit"
            )
        )
        self.assertFalse(
            self.rfhub_extractor._robot_files_candidates(
                self.fixture_path / "LibWithEmptyInit"
            )
        )

    def test_filter_keywords_no_include_no_exclude_should_return_all(self):
        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="", exclude=""
        )
        self.assertEqual(filtered_kws_list, KEYWORDDOC_WITH_TAGS)

    def test_filter_keywords_only_include_should_filter_keywords(self):
        tag1_kws = set(kw for kw in KEYWORDDOC_WITH_TAGS if "tag1" in list(kw.tags))
        tag2_kws = set(kw for kw in KEYWORDDOC_WITH_TAGS if "tag2" in list(kw.tags))

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag1", exclude=""
        )
        self.assertCountEqual(filtered_kws_list, tag1_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag2", exclude=""
        )
        self.assertCountEqual(filtered_kws_list, tag2_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag1ORnot_at_tag", exclude=""
        )
        self.assertCountEqual(filtered_kws_list, tag1_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag1ORtag2", exclude=""
        )
        self.assertCountEqual(filtered_kws_list, tag1_kws | tag2_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag1ANDtag2", exclude=""
        )
        self.assertCountEqual(filtered_kws_list, tag1_kws & tag2_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="not_a_tag", exclude=""
        )
        self.assertCountEqual(filtered_kws_list, set())

    def test_filter_keywords_only_exclude_should_filter_keywords(self):
        all_kws = set(KEYWORDDOC_WITH_TAGS)
        tag1_kws = set(kw for kw in KEYWORDDOC_WITH_TAGS if "tag1" in list(kw.tags))
        tag2_kws = set(kw for kw in KEYWORDDOC_WITH_TAGS if "tag2" in list(kw.tags))

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="", exclude="tag1"
        )
        self.assertCountEqual(filtered_kws_list, all_kws - tag1_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="", exclude="tag2"
        )
        self.assertCountEqual(filtered_kws_list, all_kws - tag2_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="", exclude="tag1ORnot_at_tag"
        )
        self.assertCountEqual(filtered_kws_list, all_kws - tag1_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="", exclude="tag1ORtag2"
        )
        self.assertCountEqual(filtered_kws_list, all_kws - (tag1_kws | tag2_kws))

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="", exclude="tag1ANDtag2"
        )
        self.assertCountEqual(filtered_kws_list, all_kws - (tag1_kws & tag2_kws))

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="", exclude="not_a_tag"
        )
        self.assertCountEqual(filtered_kws_list, all_kws)

    def test_filter_keywords_include_exclude_should_filter_keywords(self):
        tag1_kws = set(kw for kw in KEYWORDDOC_WITH_TAGS if "tag1" in list(kw.tags))
        tag2_kws = set(kw for kw in KEYWORDDOC_WITH_TAGS if "tag2" in list(kw.tags))

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag1", exclude="tag1"
        )
        self.assertCountEqual(filtered_kws_list, tag1_kws - tag1_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag1", exclude="tag2"
        )
        self.assertCountEqual(filtered_kws_list, tag1_kws - tag2_kws)

        filtered_kws_list = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag1ORtag2", exclude="tag1ANDtag2"
        )
        self.assertCountEqual(
            filtered_kws_list, (tag1_kws | tag2_kws) - (tag1_kws & tag2_kws)
        )

    def test_filter_keywords_should_be_indempotent(self):
        """
        Feeding _filter_keywords with its own output (same args) should return the same output.
        """
        filtered_kws_list1 = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="", exclude=""
        )
        filtered_kws_list2 = KeywordsExtractor._filter_keywords(
            filtered_kws_list1, include="", exclude=""
        )

        self.assertEqual(filtered_kws_list1, filtered_kws_list2)

        filtered_kws_list1 = KeywordsExtractor._filter_keywords(
            KEYWORDDOC_WITH_TAGS, include="tag1", exclude="tag2"
        )
        filtered_kws_list2 = KeywordsExtractor._filter_keywords(
            filtered_kws_list1, include="tag1", exclude="tag2"
        )

        self.assertEqual(filtered_kws_list1, filtered_kws_list2)
