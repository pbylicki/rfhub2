from starlette.requests import Request

from rfhub2.db.repository.keyword_repository import KeywordRepository
from rfhub2.db.repository.collection_repository import CollectionRepository


def get_collection_repository(request: Request) -> CollectionRepository:
    return CollectionRepository(request.state.db)


def get_keyword_repository(request: Request) -> KeywordRepository:
    return KeywordRepository(request.state.db)
