import unittest
from starlette.testclient import TestClient

from rfhub2 import config
from rfhub2.app import create_app
from rfhub2.db.migrate import migrate_db
from rfhub2.db.session import db_session, engine
from tests.unit.sample_data import recreate_data


class BaseApiEndpointTest(unittest.TestCase):

    maxDiff = None

    NESTED_COLLECTION_1 = {"id": 1, "name": "First collection"}
    NESTED_COLLECTION_2 = {"id": 2, "name": "Second collection"}
    NESTED_KEYWORD_1 = {
        "id": 1,
        "name": "Test setup",
        "doc": "Prepare test environment, use teardown after this one",
        "synopsis": "Prepare test environment, use teardown after this one",
        "html_doc": "<p>Prepare test environment, use teardown after this one</p>",
        "args": None,
        "tags": [],
        "arg_string": "",
    }
    NESTED_KEYWORD_2 = {
        "id": 2,
        "name": "Some keyword",
        "doc": "Perform some check",
        "synopsis": "Perform some check",
        "html_doc": "<p>Perform some check</p>",
        "args": None,
        "tags": [],
        "arg_string": "",
    }
    NESTED_KEYWORD_3 = {
        "id": 3,
        "name": "Teardown",
        "doc": "Clean up environment",
        "synopsis": "Clean up environment",
        "html_doc": "<p>Clean up environment</p>",
        "args": None,
        "tags": [],
        "arg_string": "",
    }
    NESTED_KEYWORD_4 = {
        "id": 4,
        "name": "zzz",
        "doc": "zzzzzz",
        "synopsis": "zzzzzz",
        "html_doc": "<p>zzzzzz</p>",
        "args": None,
        "tags": [],
        "arg_string": "",
    }
    COLLECTION_1 = {
        "id": 1,
        "keyword_count": 3,
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
        "keyword_count": 1,
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
        "keywords": [NESTED_KEYWORD_4],
    }
    COLLECTION_3 = {
        "id": 3,
        "keyword_count": 0,
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
    KEYWORD_4 = {"collection": NESTED_COLLECTION_2, **NESTED_KEYWORD_4}
    KEYWORD_TO_CREATE = {
        "name": "New Keyword",
        "doc": "New doc",
        "args": None,
        "collection_id": COLLECTION_2["id"],
    }
    KEYWORD_CREATED = {
        "id": 5,
        "name": "New Keyword",
        "doc": "New doc",
        "synopsis": "New doc",
        "html_doc": "<p>New doc</p>",
        "args": None,
        "arg_string": "",
        "tags": [],
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
        "keyword_count": 0,
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
    COLLECTION_1_WITH_STATS = {**COLLECTION_1, "times_used": 20}
    COLLECTION_2_WITH_STATS = {**COLLECTION_2, "times_used": 15}
    COLLECTION_3_WITH_STATS = {**COLLECTION_3, "times_used": None}
    KEYWORD_1_WITH_STATS = {**KEYWORD_1, "times_used": 10, "avg_elapsed": 100.0}
    KEYWORD_2_WITH_STATS = {**KEYWORD_2, "times_used": 10, "avg_elapsed": 500.0}
    KEYWORD_3_WITH_STATS = {**KEYWORD_3, "times_used": None, "avg_elapsed": None}
    KEYWORD_4_WITH_STATS = {**KEYWORD_4, "times_used": None, "avg_elapsed": None}
    STATISTICS_1 = {
        "collection": "First collection",
        "keyword": "Some keyword",
        "execution_time": "2019-12-21T02:30:00",
        "times_used": 5,
        "total_elapsed": 3000,
        "min_elapsed": 300,
        "max_elapsed": 1500,
    }
    STATISTICS_2 = {
        "collection": "First collection",
        "keyword": "Some keyword",
        "execution_time": "2019-12-20T01:30:00",
        "times_used": 5,
        "total_elapsed": 2000,
        "min_elapsed": 200,
        "max_elapsed": 1000,
    }
    STATISTICS_3 = {
        "collection": "First collection",
        "keyword": "Test setup",
        "execution_time": "2019-12-21T02:30:00",
        "times_used": 10,
        "total_elapsed": 1000,
        "min_elapsed": 10,
        "max_elapsed": 100,
    }
    STATISTICS_4 = {
        "collection": "Second collection",
        "keyword": "Old keyword",
        "execution_time": "2019-12-21T01:30:00",
        "times_used": 5,
        "total_elapsed": 2500,
        "min_elapsed": 200,
        "max_elapsed": 1000,
    }
    STATISTICS_5 = {
        **STATISTICS_4,
        "execution_time": "2019-12-21T02:30:00",
        "min_elapsed": 100,
    }
    STATISTICS_6 = {
        **STATISTICS_4,
        "execution_time": "2019-12-21T03:30:00",
        "max_elapsed": 1100,
    }

    AGGREGATED_STATS_COLLECTION_1 = {
        "times_used": 20,
        "total_elapsed": 6000,
        "avg_elapsed": 300.0,
        "min_elapsed": 10,
        "max_elapsed": 1500,
    }
    AGGREGATED_STATS_KEYWORD_2 = {
        "times_used": 10,
        "total_elapsed": 5000,
        "avg_elapsed": 500.0,
        "min_elapsed": 200,
        "max_elapsed": 1500,
    }
    AGGREGATED_STATS_OLD_KEYWORD = {
        "times_used": 10,
        "total_elapsed": 5000,
        "avg_elapsed": 500.0,
        "min_elapsed": 100,
        "max_elapsed": 1100,
    }
    AGGREGATED_STATS_EMPTY = {
        "times_used": 0,
        "total_elapsed": 0,
        "avg_elapsed": 0.0,
        "min_elapsed": 0,
        "max_elapsed": 0,
    }
    STATISTICS_TO_CREATE = {
        "collection": "First collection",
        "keyword": "Some keyword",
        "execution_time": "2019-12-22T03:30:00",
        "times_used": 5,
        "total_elapsed": 2500,
        "min_elapsed": 200,
        "max_elapsed": 1000,
    }

    @classmethod
    def setUpClass(cls) -> None:
        migrate_db(engine)

    def setUp(self) -> None:
        self.app = create_app()
        db_session.rollback()
        recreate_data(db_session)
        self.client: TestClient = TestClient(self.app)
        self.auth_client: TestClient = TestClient(self.app)
        self.auth_client.auth = (config.BASIC_AUTH_USER, config.BASIC_AUTH_PASSWORD)
