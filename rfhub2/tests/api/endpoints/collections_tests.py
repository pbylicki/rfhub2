from rfhub2.tests.api.endpoints.base_endpoint_tests import BaseApiEndpointTest


class CollectionsApiTest(BaseApiEndpointTest):

    def test_get_single_collection(self):
        response = self.client.get("api/v1/collections/1/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.COLLECTION_1)

    def test_get_404_for_nonexistent_collection_id(self):
        response = self.client.get("api/v1/collections/999/")
        self.assertEqual(response.status_code, 404)

    def test_get_all_collections(self):
        response = self.client.get("api/v1/collections/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 3)
        self.assertEqual(body[0], self.COLLECTION_1)

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
