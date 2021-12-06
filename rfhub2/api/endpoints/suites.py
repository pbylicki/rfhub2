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


@router.get("/{id}/", response_model=Suite)
def get_suite(*, repository: SuiteRepository = Depends(get_suite_repository), id: int):
    suite: Optional[DBSuite] = repository.get(id)
    return or_404(suite)


@router.post("/", response_model=Suite, status_code=201)
def create_suite(
    *,
    _: bool = Depends(is_authenticated),
    repository: SuiteRepository = Depends(get_suite_repository),
    suite_hierarchy: SuiteHierarchy,
):
    db_suite: DBSuite = repository.add(DBSuite.create(suite_hierarchy))
    return db_suite.to_hierarchy()


@router.delete("/{id}/")
def delete_suite(
    *,
    _: bool = Depends(is_authenticated),
    repository: SuiteRepository = Depends(get_suite_repository),
    id: int,
):
    deleted: int = repository.delete_hierarchy(id)
    if deleted:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)
