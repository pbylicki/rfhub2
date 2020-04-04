from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from typing import List, Optional

from rfhub2.api.utils.auth import is_authenticated
from rfhub2.api.utils.db import get_collection_repository
from rfhub2.api.utils.http import or_404
from rfhub2.api.utils.order import get_ordering
from rfhub2.db.base import Collection as DBCollection
from rfhub2.db.repository.collection_repository import CollectionRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.model import Collection, CollectionUpdate, CollectionWithStats

router = APIRouter()


@router.get("/", response_model=List[Collection])
def get_collections(
    repository: CollectionRepository = Depends(get_collection_repository),
    skip: int = 0,
    limit: int = 100,
    pattern: str = None,
    libtype: str = None,
    ordering: List[OrderingItem] = Depends(get_ordering),
):
    return repository.get_all(
        skip=skip, limit=limit, pattern=pattern, libtype=libtype, ordering=ordering
    )


@router.get("/stats/", response_model=List[CollectionWithStats])
def get_collections_with_stats(
    repository: CollectionRepository = Depends(get_collection_repository),
    skip: int = 0,
    limit: int = 100,
    pattern: str = None,
    libtype: str = None,
    ordering: List[OrderingItem] = Depends(get_ordering),
):
    return repository.get_all_with_stats(
        skip=skip, limit=limit, pattern=pattern, libtype=libtype, ordering=ordering
    )


@router.get("/stats/{id}/", response_model=CollectionWithStats)
def get_collection_with_stats(
    *, repository: CollectionRepository = Depends(get_collection_repository), id: int
):
    collection: Optional[CollectionWithStats] = repository.get_with_stats(id)
    return or_404(collection)


@router.get("/{id}/", response_model=Collection)
def get_collection(
    *, repository: CollectionRepository = Depends(get_collection_repository), id: int
):
    collection: Optional[DBCollection] = repository.get(id)
    return or_404(collection).to_model()


@router.post("/", response_model=Collection, status_code=201)
def create_collection(
    *,
    _: bool = Depends(is_authenticated),
    repository: CollectionRepository = Depends(get_collection_repository),
    collection: CollectionUpdate,
):
    db_collection: DBCollection = repository.add(DBCollection.create(collection))
    return db_collection.to_model()


@router.put("/{id}/", response_model=Collection)
def update_collection(
    *,
    _: bool = Depends(is_authenticated),
    repository: CollectionRepository = Depends(get_collection_repository),
    id: int,
    collection_update: CollectionUpdate,
):
    db_collection: DBCollection = or_404(repository.get(id))
    updated: DBCollection = repository.update(
        db_collection, collection_update.dict(exclude_unset=True)
    )
    return updated.to_model()


@router.delete("/{id}/")
def delete_collection(
    *,
    _: bool = Depends(is_authenticated),
    repository: CollectionRepository = Depends(get_collection_repository),
    id: int,
):
    deleted: int = repository.delete(id)
    if deleted:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)
