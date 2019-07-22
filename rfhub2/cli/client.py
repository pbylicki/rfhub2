from requests import session, post, get, delete, exceptions
from typing import Dict
from rfhub2.model import Collection, Keyword

PROTOCOL = 'http://'
API_V1 = 'api/v1'
TEST_COLLECTION = {"name": "a", "type": "a", "version": "a", "scope": "a",
                   "named_args": "a", "path": "a", "doc": "a", "doc_format": "a"}


class Client(object):
    """
    API client with methods to populate rfhub2 application.
    """
    def __init__(self, app_interface: str, port: int, user: str, password: str,):
        self.app_interface = app_interface
        self.port = port
        self.auth = (user, password)
        self.session = session()
        self.app_url = f'{PROTOCOL}{self.app_interface}:{self.port}'
        self.api_url = f'{self.app_url}/{API_V1}'

    def check_communication_with_app(self) -> None:
        try:
            self.get_collections()
        except exceptions.RequestException:
            print(f'Connection to application at {self.app_url} refused!\n'
                  f'Check parameters for app-interace and port.')
            exit(1)
        req_check_auth = self._post_request('collections', TEST_COLLECTION)
        if req_check_auth.status_code == 201:
            self._delete_request('collections', req_check_auth.json()["id"])
        else:
            print(f'{req_check_auth.reason}! Check used credentials.')
            exit(1)

    def get_collections(self) -> get:
        """
        Gets list of collections object using request get method.
        """
        return self._get_request(endpoint='collections')

    def add_collection(self, data: Collection) -> post:
        """
        Adds collection using request post method.
        """
        return self._post_request(endpoint='collections', data=data)

    def delete_collection(self, id: int) -> delete:
        """
        Deletes collection with given id.
        """
        self._delete_request(endpoint='collections', id=id)

    def add_keyword(self, data: Keyword) -> post:
        """
        Adds keyword using request post method.
        """
        return self._post_request(endpoint='keywords', data=data)

    def _get_request(self, endpoint: str) -> get:
        """
        Sends get request from given endpoint.
        """
        return self.session.get(url=f'{self.api_url}/{endpoint}', headers={"accept": "application/json"})

    def _post_request(self, endpoint: str, data: Dict) -> post:
        """
        Sends post request to collections or keywords endpoint.
        """
        return self.session.post(url=f'{self.api_url}/{endpoint}/', auth=self.auth, json=data,
                                 headers={"Content-Type": "application/json", "accept": "application/json"})

    def _delete_request(self, endpoint: str, id: int) -> delete:
        """
        Sends delete request to collections or keywords endpoint with item id.
        """
        return self.session.delete(url=f'{self.api_url}/{endpoint}/{id}/', auth=self.auth,
                                   headers={"accept": "application/json"})
