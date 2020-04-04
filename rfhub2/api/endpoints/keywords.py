from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from typing import List, Optional

from rfhub2.api.utils.auth import is_authenticated
from rfhub2.api.utils.db import get_collection_repository, get_keyword_repository
from rfhub2.api.utils.http import or_404
from rfhub2.api.utils.order import get_ordering
from rfhub2.db.base import Collection as DBCollection, Keyword as DBKeyword
from rfhub2.db.repository.collection_repository import CollectionRepository
from rfhub2.db.repository.keyword_repository import KeywordRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.model import Keyword, KeywordCreate, KeywordUpdate, KeywordWithStats
from rfhub2.ui.search_params import SearchParams

router = APIRouter()


@router.get("/", response_model=List[Keyword])
def get_keywords(
    repository: KeywordRepository = Depends(get_keyword_repository),
    skip: int = 0,
    limit: int = 100,
    pattern: str = None,
    use_doc: bool = True,
    collection_id: Optional[int] = None,
    ordering: List[OrderingItem] = Depends(get_ordering),
):
    return repository.get_all(
        skip=skip,
        limit=limit,
        pattern=pattern,
        collection_id=collection_id,
        use_doc=use_doc,
        ordering=ordering,
    )


@router.get("/stats/", response_model=List[KeywordWithStats])
def get_keywords_with_stats(
    repository: KeywordRepository = Depends(get_keyword_repository),
    skip: int = 0,
    limit: int = 100,
    pattern: str = None,
    use_doc: bool = True,
    collection_id: Optional[int] = None,
    ordering: List[OrderingItem] = Depends(get_ordering),
):
    return repository.get_all_with_stats(
        skip=skip,
        limit=limit,
        pattern=pattern,
        collection_id=collection_id,
        use_doc=use_doc,
        ordering=ordering,
    )


@router.get("/search/", response_model=List[Keyword])
def search_keywords(
    *,
    repository: KeywordRepository = Depends(get_keyword_repository),
    params: SearchParams = Depends(),
    skip: int = 0,
    limit: int = 100,
    ordering: List[OrderingItem] = Depends(get_ordering),
):
    return repository.get_all(
        pattern=params.pattern,
        collection_name=params.collection_name,
        use_doc=params.use_doc,
        use_tags=params.use_tags,
        skip=skip,
        limit=limit,
        ordering=ordering,
    )


@router.get("/stats/{id}/", response_model=KeywordWithStats)
def get_keyword_with_stats(
    *, repository: KeywordRepository = Depends(get_keyword_repository), id: int
):
    keyword: Optional[KeywordWithStats] = repository.get_with_stats(id)
    return or_404(keyword)


@router.get("/{id}/", response_model=Keyword)
def get_keyword(
    *, repository: KeywordRepository = Depends(get_keyword_repository), id: int
):
    keyword: Optional[DBKeyword] = repository.get(id)
    return or_404(keyword).to_model()


@router.post("/", response_model=Keyword, status_code=201)
def create_keyword(
    *,
    _: bool = Depends(is_authenticated),
    repository: KeywordRepository = Depends(get_keyword_repository),
    collection_repository: CollectionRepository = Depends(get_collection_repository),
    keyword: KeywordCreate,
):
    collection: Optional[DBCollection] = collection_repository.get(
        keyword.collection_id
    )
    if not collection:
        raise HTTPException(status_code=400, detail="Collection does not exist")
    db_keyword: DBKeyword = repository.add(DBKeyword.create(keyword))
    return db_keyword.to_model()


@router.put("/{id}/", response_model=Keyword)
def update_keyword(
    *,
    _: bool = Depends(is_authenticated),
    repository: KeywordRepository = Depends(get_keyword_repository),
    id: int,
    keyword_update: KeywordUpdate,
):
    db_keyword: DBKeyword = or_404(repository.get(id))
    updated: DBKeyword = repository.update(
        db_keyword, keyword_update.dict(exclude_unset=True)
    )
    return updated.to_model()


@router.delete("/{id}/")
def delete_keyword(
    *,
    _: bool = Depends(is_authenticated),
    repository: KeywordRepository = Depends(get_keyword_repository),
    id: int,
):
    deleted: int = repository.delete(id)
    if deleted:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)
