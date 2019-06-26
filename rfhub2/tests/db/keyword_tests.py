import unittest

from rfhub2.db.base import Keyword


class KeywordTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.keyword = Keyword(
            name="My keyword",
            doc="Keyword description\n\nFurther description",
            args='["path", "arg1"]',
            collection_id=1
        )
        cls.empty_keyword = Keyword(
            name="Empty keyword",
            collection_id=1
        )

    def test_should_get_arg_string(self):
        self.assertEqual(self.keyword.arg_string, "path, arg1")

    def test_should_get_empty_string_when_keyword_has_no_args(self):
        self.assertEqual(self.empty_keyword.arg_string, "")

    def test_should_get_keyword_synopsis(self):
        self.assertEqual(self.keyword.synopsis, "Keyword description")

    def test_should_get_empty_synopsis_when_keyword_has_no_doc(self):
        self.assertEqual(self.empty_keyword.synopsis, "")

    def test_should_get_keyword_html_doc(self):
        self.assertEqual(self.keyword.html_doc(), "<p>Keyword description</p>\n<p>Further description</p>")

    def test_should_get_empty_html_doc_when_keyword_has_no_doc(self):
        self.assertEqual(self.empty_keyword.html_doc(), "")
