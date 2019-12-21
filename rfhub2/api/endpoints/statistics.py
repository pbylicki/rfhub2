from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.responses import Response
from typing import List

from rfhub2.api.utils.auth import is_authenticated
from rfhub2.api.utils.db import get_statistics_repository
from rfhub2.db.base import Statistics as DBStatistics
from rfhub2.db.repository.statistics_repository import (
    AggregatedStatistics,
    StatisticsRepository,
)
from rfhub2.model import Statistics, StatisticsDeleted

router = APIRouter()


class DuplicatedStatisticException(HTTPException):
    def __init__(self):
        super(DuplicatedStatisticException, self).__init__(
            status_code=400,
            detail="Record already exists for provided collection, keyword and execution_time",
        )


@router.get("/aggregated/", response_model=AggregatedStatistics)
def get_aggregated(
    *,
    repository: StatisticsRepository = Depends(get_statistics_repository),
    collection: str,
    keyword: str = None,
):
    return repository.get_aggregated(collection=collection, keyword=keyword)


@router.get("/", response_model=List[Statistics])
def get_statistics(
    *,
    repository: StatisticsRepository = Depends(get_statistics_repository),
    collection: str,
    keyword: str = None,
    execution_time: datetime = None,
    skip: int = 0,
    limit: int = 100,
):
    statistics: List[DBStatistics] = repository.get_many(
        collection=collection,
        keyword=keyword,
        execution_time=execution_time,
        skip=skip,
        limit=limit,
    )
    return statistics


@router.post("/", response_model=Statistics, status_code=201)
def create_statistics(
    *,
    _: bool = Depends(is_authenticated),
    repository: StatisticsRepository = Depends(get_statistics_repository),
    statistics: Statistics,
):
    db_statistics: DBStatistics = DBStatistics(**statistics.dict())
    try:
        return repository.add(db_statistics)
    except IntegrityError:
        raise DuplicatedStatisticException()


@router.delete("/")
def delete_statistics(
    *,
    response: Response,
    _: bool = Depends(is_authenticated),
    repository: StatisticsRepository = Depends(get_statistics_repository),
    collection: str,
    keyword: str = None,
    execution_time: datetime = None,
):
    deleted: int = repository.delete_many(
        collection=collection, keyword=keyword, execution_time=execution_time
    )
    if deleted:
        response.status_code = 204
        return StatisticsDeleted(deleted=deleted)
    else:
        raise HTTPException(status_code=404)


@router.delete("/all/", status_code=204)
def delete_all_statistics(
    *,
    _: bool = Depends(is_authenticated),
    repository: StatisticsRepository = Depends(get_statistics_repository),
):
    deleted: int = repository.delete_many()
    return StatisticsDeleted(deleted=deleted)
