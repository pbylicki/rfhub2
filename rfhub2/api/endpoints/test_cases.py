from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.responses import Response
from typing import List, Optional

from rfhub2.api.utils.auth import is_authenticated
from rfhub2.api.utils.db import get_test_case_repository, get_suite_repository
from rfhub2.api.utils.http import or_404
from rfhub2.api.utils.order import get_ordering
from rfhub2.db.base import Suite as DBSuite
from rfhub2.db.base import TestCase as DBTestCase
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.suite_repository import SuiteRepository
from rfhub2.db.repository.test_case_repository import TestCaseRepository
from rfhub2.model import TestCase, TestCaseCreate

router = APIRouter()


class DuplicatedTestcaseException(HTTPException):
    def __init__(self):
        super(DuplicatedTestcaseException, self).__init__(
            status_code=400, detail="Records already exist for provided testcase"
        )


@router.get("/", response_model=List[TestCase])
def get_test_cases(
    repository: TestCaseRepository = Depends(get_test_case_repository),
    pattern: Optional[str] = None,
    suite_id: Optional[int] = None,
    use_doc: bool = True,
    use_tags: bool = False,
    skip: int = 0,
    limit: int = 100,
    ordering: List[OrderingItem] = Depends(get_ordering),
):
    return repository.get_all(
        pattern=pattern,
        suite_id=suite_id,
        use_doc=use_doc,
        use_tags=use_tags,
        skip=skip,
        limit=limit,
        ordering=ordering,
    )


@router.get("/{id}/", response_model=TestCase)
def get_test_case(
    *, repository: TestCaseRepository = Depends(get_test_case_repository), id: int
):
    testcase: Optional[DBTestCase] = repository.get(id)
    return or_404(testcase)


@router.post("/", response_model=TestCase, status_code=201)
def create_test_case(
    *,
    _: bool = Depends(is_authenticated),
    repository: TestCaseRepository = Depends(get_test_case_repository),
    suite_repository: SuiteRepository = Depends(get_suite_repository),
    test_case: TestCaseCreate,
):
    suite: Optional[DBSuite] = suite_repository.get(test_case.suite_id)
    if not suite:
        raise HTTPException(status_code=400, detail="Suite does not exist")
    try:
        db_test_case: DBTestCase = repository.add(DBTestCase.create(test_case))
        return repository.get(db_test_case.id)
    except IntegrityError:
        raise DuplicatedTestcaseException()


@router.delete("/{id}/")
def delete_test_case(
    *,
    _: bool = Depends(is_authenticated),
    repository: TestCaseRepository = Depends(get_test_case_repository),
    id: int,
):
    deleted: int = repository.delete(id)
    if deleted:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)


@router.delete("/")
def delete_all_test_cases(
    *,
    _: bool = Depends(is_authenticated),
    repository: TestCaseRepository = Depends(get_test_case_repository),
):
    deleted: int = repository.delete_all()
    if deleted:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)
