from starlette.requests import Request
from unittest.mock import Mock

from rfhub2.api.utils.db import db_healthcheck
from rfhub2.db.session import Session
from tests.api.endpoints.base_endpoint_tests import BaseApiEndpointTest


class HealthcheckApiTest(BaseApiEndpointTest):

    def test_get_successful_healthcheck_response(self):
        response = self.client.get("api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"db": "ok"})

    def test_get_failed_healthcheck_response(self):
        def mock_db_healthcheck(_: Request) -> bool:
            return False

        self.app.dependency_overrides[db_healthcheck] = mock_db_healthcheck
        response = self.client.get("api/v1/health/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"db": "failure"})

    def test_successful_db_healthcheck(self):
        request = Mock()
        request.state.db = Session()
        self.assertTrue(db_healthcheck(request))

    def test_failed_db_healthcheck(self):
        request = Mock()
        request.state.db = None
        self.assertFalse(db_healthcheck(request))
