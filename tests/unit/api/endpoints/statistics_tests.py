from tests.unit.api.endpoints.base_endpoint_tests import BaseApiEndpointTest


class StatisticsApiTest(BaseApiEndpointTest):
    def test_get_all_collection_statistics(self):
        response = self.client.get("api/v1/statistics/?collection=First collection")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), [self.STATISTICS_1, self.STATISTICS_2, self.STATISTICS_3]
        )

    def test_get_all_keyword_statistics(self):
        response = self.client.get(
            "api/v1/statistics/?collection=First collection&keyword=Some keyword"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.STATISTICS_1, self.STATISTICS_2])

    def test_get_keyword_execution_statistics(self):
        response = self.client.get(
            "api/v1/statistics/?collection=First collection&keyword=Some keyword&execution_time=2019-12-20T01:30:00Z"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.STATISTICS_2])

    def test_get_empty_list_when_no_statistic_matches(self):
        response = self.client.get(
            "api/v1/statistics/?collection=Collection&keyword=Keyword&execution_time=2019-12-20T01:30:00Z"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_aggregated_collection_statistics(self):
        response = self.client.get(
            "api/v1/statistics/aggregated/?collection=First collection"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.AGGREGATED_STATS_COLLECTION_1)

    def test_get_aggregated_keyword_statistics(self):
        response = self.client.get(
            "api/v1/statistics/aggregated/?collection=First collection&keyword=Some keyword"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.AGGREGATED_STATS_KEYWORD_2)

    def test_get_empty_aggregated_statistics_for_nonexistent_keyword(self):
        response = self.client.get(
            "api/v1/statistics/aggregated/?collection=First collection&keyword=Keyword"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.AGGREGATED_STATS_EMPTY)

    def test_create_new_statistic(self):
        response = self.auth_client.post(
            "api/v1/statistics/", json=self.STATISTICS_TO_CREATE
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.STATISTICS_TO_CREATE)

    def test_should_not_create_duplicated_statistic(self):
        response = self.auth_client.post("api/v1/statistics/", json=self.STATISTICS_2)
        self.assertEqual(response.status_code, 400)

    def test_should_not_create_new_statistic_without_auth(self):
        response = self.client.post(
            "api/v1/statistics/", json=self.STATISTICS_TO_CREATE
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_all_statistics(self):
        response = self.auth_client.delete("api/v1/statistics/all/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.json(), {"deleted": 4})

    def test_should_not_delete_all_statistics_without_auth(self):
        response = self.client.delete("api/v1/statistics/all/")
        self.assertEqual(response.status_code, 401)

    def test_delete_collection_statistics(self):
        response = self.auth_client.delete(
            "api/v1/statistics/?collection=First collection"
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.json(), {"deleted": 3})

    def test_delete_keyword_statistics(self):
        response = self.auth_client.delete(
            "api/v1/statistics/?collection=First collection&keyword=Some keyword"
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.json(), {"deleted": 2})

    def test_delete_keyword_execution_statistics(self):
        response = self.auth_client.delete(
            "api/v1/statistics/?collection=First collection&keyword=Some keyword&execution_time=2019-12-20T01:30:00Z"
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.json(), {"deleted": 1})

    def test_get_404_when_deleting_nonexistent_statistics(self):
        response = self.auth_client.delete(
            "api/v1/statistics/?collection=Collection&keyword=Keyword&execution_time=2019-12-20T01:30:00Z"
        )
        self.assertEqual(response.status_code, 404)

    def test_should_not_delete_statistics_without_auth(self):
        response = self.client.delete("api/v1/statistics/?collection=First collection")
        self.assertEqual(response.status_code, 401)
