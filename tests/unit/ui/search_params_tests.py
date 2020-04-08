import unittest

from rfhub2.ui.search_params import SearchParams


class SearchParamsTest(unittest.TestCase):
    def test_should_return_default_search_params_for_invalid_input_value(self):
        for case in (None, "", "*"):
            with self.subTest(case=case):
                result: SearchParams = SearchParams(case)
                self.assertEqual(
                    (
                        result.pattern,
                        result.collection_name,
                        result.use_doc,
                        result.use_tags,
                    ),
                    SearchParams.DEFAULT,
                )
                self.assertEqual(result.raw_pattern, case)

    def test_should_extract_search_params_for_valid_input_value(self):
        test_data = [
            ("keyword", "keyword", None, True, False),
            ("keywordin", "keywordin", None, True, False),
            ("keywordin:", "keywordin:", None, True, False),
            ("keyword in:", "keyword in:", None, True, False),
            ("keyword In:lib", "keyword", "lib", True, False),
            ("keyword in: lib", "keyword", "lib", True, False),
            ("keyword in: My Lib", "keyword", "my lib", True, False),
            ("name:keywordin:", "keywordin:", None, False, False),
            ("name: keyword in: lib", "keyword", "lib", False, False),
            ("tags: tag", "tag", None, False, True),
            ("tags:tag in: lib", "tag", "lib", False, True),
        ]
        for value, pattern, col_name, use_doc, use_tags in test_data:
            with self.subTest(pattern=value):
                result: SearchParams = SearchParams(value)
                self.assertEqual(
                    (
                        result.pattern,
                        result.collection_name,
                        result.use_doc,
                        result.use_tags,
                    ),
                    (pattern, col_name, use_doc, use_tags),
                )
                self.assertEqual(result.raw_pattern, value)
