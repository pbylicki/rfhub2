from rfhub2.config import APP_TITLE
from rfhub2.version import version
from tests.api.endpoints.base_endpoint_tests import BaseApiEndpointTest


class VersionApiTest(BaseApiEndpointTest):
    def test_get_successful_version_info_response(self):
        response = self.client.get("api/v1/version/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"title": APP_TITLE, "version": version})
