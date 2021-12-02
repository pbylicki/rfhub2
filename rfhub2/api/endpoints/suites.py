from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from typing import List, Optional

from rfhub2.api.utils.auth import is_authenticated
from rfhub2.api.utils.db import get_suite_repository
from rfhub2.api.utils.http import or_404
from rfhub2.api.utils.order import get_ordering
from rfhub2.db.base import Suite as DBSuite
from rfhub2.db.repository.collection_repository import CollectionRepository
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.suite_repository import SuiteRepository
from rfhub2.model import Suite, SuiteHierarchy

router = APIRouter()


@router.get("/", response_model=List[Suite])
def get_suites(
    repository: SuiteRepository = Depends(get_suite_repository),
    pattern: Optional[str] = None,
    parent_id: Optional[int] = None,
    root_only: bool = False,
    use_doc: bool = True,
    use_tags: bool = False,
    skip: int = 0,
    limit: int = 100,
    ordering: List[OrderingItem] = Depends(get_ordering),
):
    return repository.get_all(
        pattern=pattern,
        parent_id=parent_id,
        root_only=root_only,
        use_doc=use_doc,
        use_tags=use_tags,
        skip=skip,
        limit=limit,
        ordering=ordering,
    )


@router.post("/", response_model=Suite, status_code=201)
def create_suite(
    *,
    _: bool = Depends(is_authenticated),
    repository: SuiteRepository = Depends(get_suite_repository),
    suite: Suite,
):
    hierarchy: SuiteHierarchy = SuiteHierarchy(name=suite.name, doc=suite.doc, source=suite.source, keywords=suite.keywords, suites=suite)
    # suite = Suite()
    db_suite: DBSuite = repository.add(DBSuite.create(suite))
    db_suite