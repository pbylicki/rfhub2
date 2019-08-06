from requests import session, post, get, delete, exceptions
from typing import Dict, List

from rfhub2.model import Collection, Keyword


API_V1 = 'api/v1'
TEST_COLLECTION = {"name": "healtcheck_collection", "type": "a", "version": "a", "scope": "a",
                   "named_args": "a", "path": "a", "doc": "a", "doc_format": "a"}


class Client(object):
    """
    API client with methods to populate rfhub2 application.
    """
    def __init__(self, app_url: str, user: str, password: str):
        self.app_url = app_url
        self.session = session()
        self.api_url = f'{self.app_url}/{API_V1}'
        self.session.auth = (user, password)
        self.session.headers = {"Content-Type": "application/json", "accept": "application/json"}

    def check_communication_with_app(self) -> None:
        try:
            self.get_collections()
        except exceptions.RequestException:
            print(f'Connection to application at {self.app_url} refused!\n'
                  f'Check parameter for app_url.')
            exit(1)
        req_check_auth = self._post_request('collections', TEST_COLLECTION)
        if req_check_auth['name'] == 'healtcheck_collection':
            self._delete_request('collections', req_check_auth["id"])
        else:
            print('Check used credentials!')
            exit(1)

    def get_collections(self) -> List[Collection]:
        """
        Gets list of collections object using request get method.
        """
        return self._get_request(endpoint='collections')

    def add_collection(self, data: Collection) -> Collection:
        """
        Adds collection using request post method.
        """
        return self._post_request(endpoint='collections', data=data)

    def delete_collection(self, id: int) -> delete:
        """
        Deletes collection with given id.
        """
        return self._delete_request(endpoint='collections', id=id)

    def add_keyword(self, data: Keyword) -> Keyword:
        """
        Adds keyword using request post method.
        """
        return self._post_request(endpoint='keywords', data=data)

    def _get_request(self, endpoint: str) -> get:
        """
        Sends get request from given endpoint.
        """
        request = self.session.get(url=f'{self.api_url}/{endpoint}/')
        return request.json()

    def _post_request(self, endpoint: str, data: Dict) -> post:
        """
        Sends post request to collections or keywords endpoint.
        """
        request = self.session.post(url=f'{self.api_url}/{endpoint}/', json=data)
        return request.json()

    def _delete_request(self, endpoint: str, id: int) -> delete:
        """
        Sends delete request to collections or keywords endpoint with item id.
        """
        return self.session.delete(url=f'{self.api_url}/{endpoint}/{id}/')
