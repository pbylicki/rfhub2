from pathlib import Path
import unittest
from starlette.testclient import TestClient

from rfhub2.app import create_app


class UIRouterTest(unittest.TestCase):

    INDEX_FILE = (
        Path(__file__).parent
        / ".."
        / ".."
        / ".."
        / "rfhub2"
        / "templates"
        / "index.html"
    )

    def setUp(self) -> None:
        self.app = create_app()
        self.client: TestClient = TestClient(self.app)

    def test_ui_routes_should_get_index_html_file(self):
        with open(self.INDEX_FILE) as f:
            expected_body = f.read()
        routes = ("/", "/search/?q=a", "/keywords/123/", "/keywords/123/456/")
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.text, expected_body)
