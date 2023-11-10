from requests import session, Response
from typing import Dict, Tuple, Optional

from rfhub2.model import (
    CollectionUpdate,
    KeywordCreate,
    KeywordStatisticsList,
    SuiteHierarchy,
    TestCaseCreate,
)

API_V1 = "api/v1"
TEST_COLLECTION = {
    "name": "healthcheck_collection",
    "type": "a",
    "version": "a",
    "scope": "a",
    "named_args": "a",
    "path": "a",
    "doc": "a",
    "doc_format": "a",
}


class Client(object):
    """
    API client with methods to populate rfhub2 application.
    """

    def __init__(self, app_url: str, user: str, password: str):
        self.app_url = app_url
        self.session = session()
        self.api_url = f"{self.app_url}/{API_V1}"
        self.session.auth = (user, password)
        self.session.headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }

    def get_collections(self, skip: int = 0, limit: int = 100) -> Dict:
        """
        Gets list of collections object using request get method.
        """
        return self._get_request(
            endpoint="collections", params={"skip": skip, "limit": limit}
        )

    def add_collection(self, data: CollectionUpdate) -> Tuple[int, Dict]:
        """
        Adds collection using request post method.
        """
        return self._post_request(endpoint="collections", data=data.json())

    def delete_collection(self, id: int) -> Response:
        """
        Deletes collection with given id.
        """
        return self._delete_request(endpoint="collections", id=id)

    def delete_all_collections(self) -> Response:
        """
        Deletes all collections.
        """
        return self._delete_request(endpoint="collections")

    def add_keyword(self, data: KeywordCreate) -> Tuple[int, Dict]:
        """
        Adds keyword using request post method.
        """
        return self._post_request(endpoint="keywords", data=data.json())

    def add_statistics(self, data: KeywordStatisticsList) -> Tuple[int, Dict]:
        """
        Adds statistics using requests post method.
        """
        return self._post_request(endpoint="statistics/keywords", data=data.json())

    def add_test_suites(self, data: SuiteHierarchy) -> Tuple[int, Dict]:
        """
        Adds test suites using requests post method.
        """
        return self._post_request(endpoint="suites", data=data.json())

    def delete_test_suites(self, id: int) -> Response:
        """
        Deletes test suites with given id.
        """
        return self._delete_request(endpoint="suites", id=id)

    def delete_all_test_suites(self) -> Response:
        """
        Deletes all test suites.
        """
        return self._delete_request(endpoint="suites")

    def add_test_case(self, data: TestCaseCreate) -> Tuple[int, Dict]:
        """
        Adds test case using requests post method.
        """
        return self._post_request(endpoint="test_cases", data=data.json())

    def delete_test_case(self, id: int) -> Response:
        """
        Deletes test case with given id.
        """
        return self._delete_request(endpoint="test_cases", id=id)

    def delete_all_test_cases(self) -> Response:
        """
        Deletes all test cases.
        """
        return self._delete_request(endpoint="test_cases")

    def _get_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Sends get request from given endpoint.
        """
        request = self.session.get(url=f"{self.api_url}/{endpoint}/", params=params)
        return request.json()

    def _post_request(self, endpoint: str, data: str) -> Tuple[int, Dict]:
        """
        Sends post request to collections or keywords endpoint.
        """
        request = self.session.post(url=f"{self.api_url}/{endpoint}/", data=data)
        return request.status_code, request.json()

    def _delete_request(self, endpoint: str, id: Optional[int] = None) -> Response:
        """
        Sends delete request to collections or keywords endpoint with item id.
        If no id provided then deletes all collections.
        """
        if id:
            return self.session.delete(url=f"{self.api_url}/{endpoint}/{id}/")
        else:
            return self.session.delete(url=f"{self.api_url}/{endpoint}/")
