from tests.unit.api.endpoints.base_endpoint_tests import BaseApiEndpointTest


class KeywordsApiTest(BaseApiEndpointTest):
    def test_get_single_keyword(self):
        response = self.client.get("api/v1/keywords/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.KEYWORD_1)

    def test_get_single_keyword_with_statistics(self):
        response = self.client.get("api/v1/keywords/stats/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.KEYWORD_1_WITH_STATS)

    def test_get_404_for_nonexistent_keyword_id(self):
        response = self.client.get("api/v1/keywords/999/")
        self.assertEqual(response.status_code, 404)

    def test_get_all_keywords(self):
        response = self.client.get("api/v1/keywords/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 4)
        self.assertEqual(
            body, [self.KEYWORD_2, self.KEYWORD_3, self.KEYWORD_1, self.KEYWORD_4]
        )

    def test_get_all_keywords_with_collection_id(self):
        response = self.client.get(
            f"api/v1/keywords/?collection_id={self.COLLECTION_1['id']}"
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 3)
        self.assertEqual(body, [self.KEYWORD_2, self.KEYWORD_3, self.KEYWORD_1])

    def test_get_all_keywords_with_limit(self):
        response = self.client.get("api/v1/keywords?limit=2")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body, [self.KEYWORD_2, self.KEYWORD_3])

    def test_get_all_keywords_with_skip(self):
        response = self.client.get("api/v1/keywords?skip=1")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 3)
        self.assertEqual(body, [self.KEYWORD_3, self.KEYWORD_1, self.KEYWORD_4])

    def test_get_all_keywords_with_skip_and_limit(self):
        response = self.client.get("api/v1/keywords?skip=1&limit=1")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body, [self.KEYWORD_3])

    def test_get_all_keywords_with_filter_pattern(self):
        response = self.client.get("api/v1/keywords?pattern=teardown")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body, [self.KEYWORD_3, self.KEYWORD_1])

    def test_get_all_keywords_with_filter_pattern_not_using_doc(self):
        response = self.client.get("api/v1/keywords?pattern=teardown&use_doc=false")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body, [self.KEYWORD_3])

    def test_get_all_keywords_with_custom_ordering(self):
        response = self.client.get("api/v1/keywords?order=doc")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(
            body, [self.KEYWORD_3, self.KEYWORD_2, self.KEYWORD_1, self.KEYWORD_4]
        )

    def test_get_all_keywords_with_statistics(self):
        response = self.client.get("api/v1/keywords/stats/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 4)
        self.assertEqual(
            body,
            [
                self.KEYWORD_2_WITH_STATS,
                self.KEYWORD_3_WITH_STATS,
                self.KEYWORD_1_WITH_STATS,
                self.KEYWORD_4_WITH_STATS,
            ],
        )

    def test_get_all_keywords_with_statistics_with_collection_id(self):
        response = self.client.get(
            f"api/v1/keywords/stats/?collection_id={self.COLLECTION_1['id']}"
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 3)
        self.assertEqual(
            body,
            [
                self.KEYWORD_2_WITH_STATS,
                self.KEYWORD_3_WITH_STATS,
                self.KEYWORD_1_WITH_STATS,
            ],
        )

    def test_search_keywords(self):
        response = self.client.get(
            "api/v1/keywords/search?pattern=name:%20teardown%20in:%20first"
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body, [self.KEYWORD_3])

    def test_search_keywords_without_results(self):
        response = self.client.get(
            "api/v1/keywords/search?pattern=name:%20teardown%20in:%20second"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_search_keywords_without_pattern_should_get_all(self):
        response = self.client.get("api/v1/keywords/search/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [self.KEYWORD_2, self.KEYWORD_3, self.KEYWORD_1, self.KEYWORD_4],
        )

    def test_search_keywords_with_skip_and_limit(self):
        cases = [
            (
                "api/v1/keywords/search?pattern=teardown%20in:%20first&skip=1",
                [self.KEYWORD_1],
            ),
            (
                "api/v1/keywords/search?pattern=teardown%20in:%20first&limit=1",
                [self.KEYWORD_3],
            ),
        ]
        for url, results in cases:
            with self.subTest(url=url, results=results):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), results)

    def test_get_empty_list_with_nonexistent_filter_pattern(self):
        response = self.client.get("api/v1/keywords?pattern=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_create_new_keyword_for_existing_collection(self):
        response = self.auth_client.post(
            "api/v1/keywords/", json=self.KEYWORD_TO_CREATE
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.KEYWORD_CREATED)

    def test_should_not_create_new_keyword_for_existing_collection_without_auth(self):
        response = self.client.post("api/v1/keywords/", json=self.KEYWORD_TO_CREATE)
        self.assertEqual(response.status_code, 401)

    def test_get_400_when_creating_new_keyword_for_nonexistent_collection(self):
        keyword_to_create = {**self.KEYWORD_TO_CREATE, "collection_id": 999}
        response = self.auth_client.post("api/v1/keywords/", json=keyword_to_create)
        self.assertEqual(response.status_code, 400)

    def test_update_existing_keyword(self):
        response = self.auth_client.put(
            f"api/v1/keywords/{self.KEYWORD_3['id']}/", json=self.KEYWORD_TO_UPDATE
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.KEYWORD_UPDATED)

    def test_should_not_update_existing_keyword_without_auth(self):
        response = self.client.put(
            f"api/v1/keywords/{self.KEYWORD_3['id']}/", json=self.KEYWORD_TO_UPDATE
        )
        self.assertEqual(response.status_code, 401)

    def test_get_404_when_updating_nonexistent_keyword(self):
        response = self.auth_client.put(
            "api/v1/keywords/999/", json=self.KEYWORD_TO_UPDATE
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_existing_keyword(self):
        response = self.auth_client.delete("api/v1/keywords/1/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.text, "")
        response = self.auth_client.get("api/v1/keywords/")
        self.assertEqual(len(response.json()), 3)

    def test_should_not_delete_existing_keyword_without_auth(self):
        response = self.client.delete("api/v1/keywords/1/")
        self.assertEqual(response.status_code, 401)

    def test_get_404_when_deleting_nonexistent_keyword(self):
        response = self.auth_client.delete("api/v1/keywords/999/")
        self.assertEqual(response.status_code, 404)
