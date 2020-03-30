from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.responses import Response
from typing import List

from rfhub2.api.utils.auth import is_authenticated
from rfhub2.api.utils.db import get_keyword_statistics_repository
from rfhub2.api.utils.order import get_ordering
from rfhub2.db.base import KeywordStatistics as DBStatistics
from rfhub2.db.repository.ordering import OrderingItem
from rfhub2.db.repository.keyword_statistics_repository import (
    AggregatedKeywordStatistics,
    KeywordStatisticsFilterParams,
    KeywordStatisticsRepository,
)
from rfhub2.model import KeywordStatistics, StatisticsDeleted, StatisticsInserted

router = APIRouter()


class DuplicatedStatisticsException(HTTPException):
    def __init__(self):
        super(DuplicatedStatisticsException, self).__init__(
            status_code=400,
            detail="Records already exist for provided collection, keyword and execution_time",
        )


@router.get("/aggregated/", response_model=AggregatedKeywordStatistics)
def get_aggregated(
    *,
    repository: KeywordStatisticsRepository = Depends(
        get_keyword_statistics_repository
    ),
    filter_params: KeywordStatisticsFilterParams = Depends(),
):
    return repository.get_aggregated(filter_params)


@router.get("/", response_model=List[KeywordStatistics])
def get_statistics(
    *,
    repository: KeywordStatisticsRepository = Depends(
        get_keyword_statistics_repository
    ),
    filter_params: KeywordStatisticsFilterParams = Depends(),
    skip: int = 0,
    limit: int = 100,
    ordering: List[OrderingItem] = Depends(get_ordering),
):
    return repository.get_many(
        filter_params=filter_params, skip=skip, limit=limit, ordering=ordering
    )


@router.post("/", status_code=201)
def create_statistics(
    *,
    _: bool = Depends(is_authenticated),
    repository: KeywordStatisticsRepository = Depends(
        get_keyword_statistics_repository
    ),
    statistics: List[KeywordStatistics],
):
    db_statistics: List[DBStatistics] = [
        DBStatistics.create(stat) for stat in statistics
    ]
    try:
        inserted: int = repository.add_many(db_statistics)
        return StatisticsInserted(inserted=inserted)
    except IntegrityError:
        raise DuplicatedStatisticsException()


@router.delete("/")
def delete_statistics(
    *,
    response: Response,
    _: bool = Depends(is_authenticated),
    repository: KeywordStatisticsRepository = Depends(
        get_keyword_statistics_repository
    ),
    filter_params: KeywordStatisticsFilterParams = Depends(),
):
    deleted: int = repository.delete_many(filter_params)
    if deleted:
        response.status_code = 204
        return StatisticsDeleted(deleted=deleted)
    else:
        raise HTTPException(status_code=404)


@router.delete("/all/", status_code=204)
def delete_all_statistics(
    *,
    _: bool = Depends(is_authenticated),
    repository: KeywordStatisticsRepository = Depends(
        get_keyword_statistics_repository
    ),
):
    deleted: int = repository.delete_many()
    return StatisticsDeleted(deleted=deleted)
