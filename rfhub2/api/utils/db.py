from starlette.requests import Request

from rfhub2.db.repository.keyword_repository import KeywordRepository
from rfhub2.db.repository.collection_repository import CollectionRepository
from rfhub2.db.repository.keyword_statistics_repository import (
    KeywordStatisticsRepository,
)
from rfhub2.db.repository.suite_repository import SuiteRepository


def get_collection_repository(request: Request) -> CollectionRepository:
    return CollectionRepository(request.state.db)


def get_keyword_repository(request: Request) -> KeywordRepository:
    return KeywordRepository(request.state.db)


def get_keyword_statistics_repository(request: Request) -> KeywordStatisticsRepository:
    return KeywordStatisticsRepository(request.state.db)


def get_suite_repository(request: Request) -> SuiteRepository:
    return SuiteRepository(request.state.db)


def db_healthcheck(request: Request) -> bool:
    try:
        result = request.state.db.execute("select 1")
        return next(result) == (1,)
    except Exception as e:
        print(e)
        return False
