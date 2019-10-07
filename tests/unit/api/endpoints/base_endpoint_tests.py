import unittest
from starlette.testclient import TestClient

from rfhub2 import config
from rfhub2.app import create_app
from rfhub2.db.init_db import init_db
from rfhub2.db.sample_data import recreate_data
from rfhub2.db.session import db_session


class BaseApiEndpointTest(unittest.TestCase):

    NESTED_COLLECTION_1 = {"id": 1, "name": "First collection"}
    NESTED_KEYWORD_1 = {
        "id": 1,
        "name": "Test setup",
        "doc": "Prepare test environment, use teardown after this one",
        "synopsis": "Prepare test environment, use teardown after this one",
        "html_doc": "<p>Prepare test environment, use teardown after this one</p>",
        "args": None,
        "arg_string": "",
    }
    NESTED_KEYWORD_2 = {
        "id": 2,
        "name": "Some keyword",
        "doc": "Perform some check",
        "synopsis": "Perform some check",
        "html_doc": "<p>Perform some check</p>",
        "args": None,
        "arg_string": "",
    }
    NESTED_KEYWORD_3 = {
        "id": 3,
        "name": "Teardown",
        "doc": "Clean up environment",
        "synopsis": "Clean up environment",
        "html_doc": "<p>Clean up environment</p>",
        "args": None,
        "arg_string": "",
    }
    COLLECTION_1 = {
        "id": 1,
        "name": "First collection",
        "type": "robot",
        "version": None,
        "scope": None,
        "named_args": None,
        "path": None,
        "doc": None,
        "doc_format": None,
        "synopsis": "",
        "html_doc": "",
        "keywords": [NESTED_KEYWORD_2, NESTED_KEYWORD_3, NESTED_KEYWORD_1],
    }
    COLLECTION_2 = {
        "id": 2,
        "name": "Second collection",
        "type": "Robot",
        "version": None,
        "scope": None,
        "named_args": None,
        "path": None,
        "doc": None,
        "doc_format": None,
        "synopsis": "",
        "html_doc": "",
        "keywords": [],
    }
    COLLECTION_3 = {
        "id": 3,
        "name": "Third",
        "type": "Library",
        "version": None,
        "scope": None,
        "named_args": None,
        "path": None,
        "doc": None,
        "doc_format": None,
        "synopsis": "",
        "html_doc": "",
        "keywords": [],
    }
    KEYWORD_1 = {"collection": NESTED_COLLECTION_1, **NESTED_KEYWORD_1}
    KEYWORD_2 = {"collection": NESTED_COLLECTION_1, **NESTED_KEYWORD_2}
    KEYWORD_3 = {"collection": NESTED_COLLECTION_1, **NESTED_KEYWORD_3}
    KEYWORD_TO_CREATE = {
        "name": "New Keyword",
        "doc": "New doc",
        "args": None,
        "collection_id": COLLECTION_2["id"],
    }
    KEYWORD_CREATED = {
        "id": 4,
        "name": "New Keyword",
        "doc": "New doc",
        "synopsis": "New doc",
        "html_doc": "<p>New doc</p>",
        "args": None,
        "arg_string": "",
        "collection": {"id": COLLECTION_2["id"], "name": COLLECTION_2["name"]},
    }
    KEYWORD_TO_UPDATE = {
        "name": "Updated Teardown",
        "doc": "Updated Clean up environment",
        "synopsis": "Updated Clean up environment",
        "html_doc": "<p>Updated Clean up environment</p>",
    }
    KEYWORD_UPDATED = {**KEYWORD_3, **KEYWORD_TO_UPDATE}
    COLLECTION_TO_CREATE = {
        "name": "New Resource",
        "type": "Resource",
        "version": "1.0.2",
        "scope": None,
        "named_args": "conn_string",
        "path": "/some/file",
        "doc": "New Resource collection",
        "doc_format": None,
    }
    COLLECTION_CREATED = {
        **COLLECTION_TO_CREATE,
        "id": 4,
        "synopsis": "New Resource collection",
        "html_doc": "<p>New Resource collection</p>",
        "keywords": [],
    }
    COLLECTION_TO_UPDATE = {
        "name": "Updated collection",
        "version": "1.0.2-NEW",
        "path": "/some/file",
    }
    COLLECTION_UPDATED = {**COLLECTION_3, **COLLECTION_TO_UPDATE}

    def setUp(self) -> None:
        self.app = create_app()
        db_session.rollback()
        init_db(db_session)
        recreate_data(db_session)
        self.client: TestClient = TestClient(self.app)
        self.auth_client: TestClient = TestClient(self.app)
        self.auth_client.auth = (config.BASIC_AUTH_USER, config.BASIC_AUTH_PASSWORD)
