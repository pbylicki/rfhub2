import unittest
from starlette.testclient import TestClient

from rfhub2.app import create_app
from rfhub2.db.init_db import init_db
from rfhub2.db.sample_data import recreate_data
from rfhub2.db.session import db_session


class BaseApiEndpointTest(unittest.TestCase):

    NESTED_COLLECTION_1 = {
        'id': 1,
        'name': 'First collection'
    }
    NESTED_KEYWORD_1 = {
        'id': 1,
        'name': 'Test setup',
        'doc': 'Prepare test environment, use teardown after this one',
        'args': None
    }
    NESTED_KEYWORD_2 = {
        'id': 2,
        'name': 'Some keyword',
        'doc': 'Perform some check',
        'args': None
    }
    NESTED_KEYWORD_3 = {
        'id': 3,
        'name': 'Teardown',
        'doc': 'Clean up environment',
        'args': None
    }
    COLLECTION_1 = {
        'id': 1,
        'name': 'First collection',
        'type': 'robot',
        'version': None,
        'scope': None,
        'named_args': None,
        'path': None,
        'doc': None,
        'doc_format': None,
        'keywords': [NESTED_KEYWORD_1, NESTED_KEYWORD_2, NESTED_KEYWORD_3]
    }
    COLLECTION_2 = {
        'id': 2,
        'name': 'Second collection',
        'type': 'Robot',
        'version': None,
        'scope': None,
        'named_args': None,
        'path': None,
        'doc': None,
        'doc_format': None,
        'keywords': []
    }
    COLLECTION_3 = {
        'id': 3,
        'name': 'Third',
        'type': 'Library',
        'version': None,
        'scope': None,
        'named_args': None,
        'path': None,
        'doc': None,
        'doc_format': None,
        'keywords': []
    }
    KEYWORD_1 = {
        'collection': NESTED_COLLECTION_1,
        **NESTED_KEYWORD_1
    }
    KEYWORD_2 = {
        'collection': NESTED_COLLECTION_1,
        **NESTED_KEYWORD_2
    }
    KEYWORD_3 = {
        'collection': NESTED_COLLECTION_1,
        **NESTED_KEYWORD_3
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = create_app()
        db_session.rollback()
        init_db(db_session)
        recreate_data(db_session)

    def setUp(self) -> None:
        self.client: TestClient = TestClient(self.app)
