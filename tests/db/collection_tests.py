import unittest

from rfhub2.db.base import Collection


class CollectionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.collection = Collection(
            name="My collection",
            doc="Collection description\n\nFurther description"
        )
        cls.empty_collection = Collection(
            name="Empty collection"
        )

    def test_should_get_collection_synopsis(self):
        self.assertEqual(self.collection.synopsis, "Collection description")

    def test_should_get_empty_synopsis_when_collection_has_no_doc(self):
        self.assertEqual(self.empty_collection.synopsis, "")

    def test_should_get_collection_html_doc(self):
        self.assertEqual(self.collection.html_doc, "<p>Collection description</p>\n<p>Further description</p>")

    def test_should_get_empty_html_doc_when_collection_has_no_doc(self):
        self.assertEqual(self.empty_collection.html_doc, "")
