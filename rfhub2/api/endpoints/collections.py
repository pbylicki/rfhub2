from fastapi import APIRouter, Depends
from typing import List, Optional

from rfhub2.api.utils.db import get_collection_repository
from rfhub2.api.utils.http import or_404
from rfhub2.db.repository.collection_repository import CollectionRepository
from rfhub2.model import Collection

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
