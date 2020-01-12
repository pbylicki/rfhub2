from tests.unit.api.endpoints.base_endpoint_tests import BaseApiEndpointTest


class CollectionsApiTest(BaseApiEndpointTest):
    def test_get_single_collection(self):
        response = self.client.get("api/v1/collections/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.COLLECTION_1)

    def test_get_single_collection_with_statistics(self):
        response = self.client.get("api/v1/collections/stats/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.COLLECTION_1_WITH_STATS)

    def test_get_404_for_nonexistent_collection_id(self):
        response = self.client.get("api/v1/collections/999/")
        self.assertEqual(response.status_code, 404)

    def test_get_all_collections(self):
        response = self.client.get("api/v1/collections/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 3)
        self.assertEqual(
            body, [self.COLLECTION_1, self.COLLECTION_2, self.COLLECTION_3]
        )

    def test_get_all_collections_with_limit(self):
        response = self.client.get("api/v1/collections?limit=2")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0], self.COLLECTION_1)

    def test_get_all_collections_with_skip(self):
        response = self.client.get("api/v1/collections?skip=1")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0], self.COLLECTION_2)

    def test_get_all_collections_with_skip_and_limit(self):
        response = self.client.get("api/v1/collections?skip=1&limit=1")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0], self.COLLECTION_2)

    def test_get_all_collections_with_filter_pattern(self):
        response = self.client.get("api/v1/collections?pattern=collection")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0], self.COLLECTION_1)

    def test_get_all_collections_with_filter_libtype(self):
        response = self.client.get("api/v1/collections?libtype=robot")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0], self.COLLECTION_1)

    def test_get_empty_list_with_nonexistent_filter_pattern(self):
        response = self.client.get("api/v1/collections?pattern=nonexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_get_all_collections_with_statistics(self):
        response = self.client.get("api/v1/collections/stats/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 3)
        self.assertEqual(
            body,
            [
                self.COLLECTION_1_WITH_STATS,
                self.COLLECTION_2_WITH_STATS,
                self.COLLECTION_3_WITH_STATS,
            ],
        )

    def test_create_new_collection(self):
        response = self.auth_client.post(
            "api/v1/collections/", json=self.COLLECTION_TO_CREATE
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), self.COLLECTION_CREATED)

    def test_should_not_create_new_collection_without_auth(self):
        response = self.client.post(
            "api/v1/collections/", json=self.COLLECTION_TO_CREATE
        )
        self.assertEqual(response.status_code, 401)

    def test_should_not_create_new_collection_with_wrong_credentials(self):
        credentials = ("rfhub", "wrong_password")
        response = self.client.post(
            "api/v1/collections/", json=self.COLLECTION_TO_CREATE, auth=credentials
        )
        self.assertEqual(response.status_code, 401)

    def test_update_existing_collection(self):
        response = self.auth_client.put(
            f"api/v1/collections/{self.COLLECTION_3['id']}/",
            json=self.COLLECTION_TO_UPDATE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.COLLECTION_UPDATED)

    def test_should_not_update_existing_collection_without_auth(self):
        response = self.client.put(
            f"api/v1/collections/{self.COLLECTION_3['id']}/",
            json=self.COLLECTION_TO_UPDATE,
        )
        self.assertEqual(response.status_code, 401)

    def test_get_404_when_updating_nonexistent_collection(self):
        response = self.auth_client.put(
            "api/v1/collections/999/", json=self.COLLECTION_TO_UPDATE
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_existing_collection(self):
        response = self.auth_client.delete("api/v1/collections/1/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.text, "")
        response = self.auth_client.get("api/v1/collections/")
        self.assertEqual(len(response.json()), 2)

    def test_should_not_delete_existing_collection_without_auth(self):
        response = self.client.delete("api/v1/collections/1/")
        self.assertEqual(response.status_code, 401)

    def test_get_404_when_deleting_nonexistent_collection(self):
        response = self.auth_client.delete("api/v1/collections/999/")
        self.assertEqual(response.status_code, 404)
