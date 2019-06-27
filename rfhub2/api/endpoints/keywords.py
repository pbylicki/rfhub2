from fastapi import APIRouter, Depends
from typing import List, Optional

from rfhub2.api.utils.db import get_keyword_repository
from rfhub2.api.utils.http import or_404
from rfhub2.db.repository.keyword_repository import KeywordRepository
from rfhub2.model import Keyword

router = APIRouter()


@router.get("/", response_model=List[Keyword])
def get_keywords(repository: KeywordRepository = Depends(get_keyword_repository),
                 skip: int = 0,
                 limit: int = 100,
                 pattern: str = None,
                 use_doc: bool = True):
    keywords: List[Keyword] = repository.get_all(skip=skip, limit=limit, pattern=pattern, use_doc=use_doc)
    return keywords


@router.get("/{id}/", response_model=Keyword)
def get_keyword(*, repository: KeywordRepository = Depends(get_keyword_repository),
                id: int):
    keyword: Optional[Keyword] = repository.get(id)
    return or_404(keyword)
