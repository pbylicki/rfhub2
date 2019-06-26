from rfhub2.tests.api.endpoints.base_endpoint_tests import BaseApiEndpointTest


class KeywordsApiTest(BaseApiEndpointTest):

    def test_get_single_keyword(self):
        response = self.client.get("api/v1/keywords/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.KEYWORD_1)

    def test_get_404_for_nonexistent_keyword_id(self):
        response = self.client.get("api/v1/keywords/999/")
        self.assertEqual(response.status_code, 404)

    def test_get_all_keywords(self):
        response = self.client.get("api/v1/keywords/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 3)
        self.assertEqual(body[0], self.KEYWORD_1)

    def test_get_all_keywords_with_limit(self):
        response = self.client.get("api/v1/keywords?limit=2")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0], self.KEYWORD_1)

    def test_get_all_keywords_with_skip(self):
        response = self.client.get("api/v1/keywords?skip=1")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0], self.KEYWORD_2)

    def test_get_all_keywords_with_skip_and_limit(self):
        response = self.client.get("api/v1/keywords?skip=1&limit=1")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0], self.KEYWORD_2)

    def test_get_all_keywords_with_filter_pattern(self):
        response = self.client.get("api/v1/keywords?pattern=teardown")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0], self.KEYWORD_1)

    def test_get_all_keywords_with_filter_pattern_not_using_doc(self):
        response = self.client.get("api/v1/keywords?pattern=teardown&use_doc=false")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0], self.KEYWORD_3)

    def test_get_empty_list_with_nonexistent_filter_pattern(self):
        response = self.client.get("api/v1/keywords?pattern=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
