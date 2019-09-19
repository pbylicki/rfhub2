import unittest

from rfhub2.ui.search_params import SearchParams


class SearchParamsTest(unittest.TestCase):
    def test_should_return_default_search_params_for_invalid_input_value(self):
        for case in (None, "", "*"):
            with self.subTest(case=case):
                result: SearchParams = SearchParams(case)
                self.assertEqual(
                    (result.pattern, result.collection_name, result.use_doc),
                    SearchParams.DEFAULT,
                )
                self.assertEqual(result.raw_pattern, case)

    def test_should_extract_search_params_for_valid_input_value(self):
        test_data = [
            ("keyword", "keyword", None, True),
            ("keywordin", "keywordin", None, True),
            ("keywordin:", "keywordin:", None, True),
            ("keyword in:", "keyword in:", None, True),
            ("keyword In:lib", "keyword", "lib", True),
            ("keyword in: lib", "keyword", "lib", True),
            ("keyword in: My Lib", "keyword", "my lib", True),
            ("name:keywordin:", "keywordin:", None, False),
            ("name: keyword in: lib", "keyword", "lib", False),
        ]
        for value, pattern, col_name, use_doc in test_data:
            with self.subTest(pattern=value):
                result: SearchParams = SearchParams(value)
                self.assertEqual(
                    (result.pattern, result.collection_name, result.use_doc),
                    (pattern, col_name, use_doc),
                )
                self.assertEqual(result.raw_pattern, value)
