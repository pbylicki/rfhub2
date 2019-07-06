from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from typing import List, Optional

from rfhub2.api.utils.db import get_collection_repository
from rfhub2.api.utils.http import or_404
from rfhub2.db.base import Collection as DBCollection
from rfhub2.db.repository.collection_repository import CollectionRepository
from rfhub2.model import Collection, CollectionUpdate

router = APIRouter()


@router.get("/", response_model=List[Collection])
def get_collections(repository: CollectionRepository = Depends(get_collection_repository),
                    skip: int = 0,
                    limit: int = 100,
                    pattern: str = None,
                    libtype: str = None):
    collections: List[Collection] = repository.get_all(skip=skip, limit=limit, pattern=pattern, libtype=libtype)
    return collections


@router.get("/{id}/", response_model=Collection)
def get_collection(*, repository: CollectionRepository = Depends(get_collection_repository),
                   id: int):
    collection: Optional[Collection] = repository.get(id)
    return or_404(collection)


@router.post("/", response_model=Collection, status_code=201)
def create_collection(*, repository: CollectionRepository = Depends(get_collection_repository),
                      collection: CollectionUpdate):
    db_collection = DBCollection(**collection.dict())
    return repository.add(db_collection)


@router.put("/{id}/", response_model=Collection)
def update_collection(*, repository: CollectionRepository = Depends(get_collection_repository),
                      id: int,
                      collection_update: CollectionUpdate):
    db_collection: DBCollection = or_404(repository.get(id))
    updated: DBCollection = repository.update(db_collection, collection_update.dict(skip_defaults=True))
    return updated


@router.delete("/{id}/")
def delete_collection(*, repository: CollectionRepository = Depends(get_collection_repository),
                      id: int):
    deleted: int = repository.delete(id)
    if deleted:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)
