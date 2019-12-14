from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from typing import List, Optional

from rfhub2.api.utils.auth import is_authenticated
from rfhub2.api.utils.db import get_statistics_repository
from rfhub2.api.utils.http import or_404
from rfhub2.db.base import Statistics as DBStatistics
from rfhub2.db.repository.statistics_repository import StatisticsRepository
from rfhub2.model import Statistics, StatisticsUpdate

router = APIRouter()


@router.get("/", response_model=List[Statistics])
def get_statistics(
    repository: StatisticsRepository = Depends(get_statistics_repository),
    skip: int = 0,
    limit: int = 100,
    pattern: str = None,
    libtype: str = None,
):
    statistics: List[DBStatistics] = repository.get_all(
        skip=skip, limit=limit, pattern=pattern, libtype=libtype
    )
    return statistics


@router.get("/{id}/", response_model=Statistics)
def get_statistics(
    *, repository: StatisticsRepository = Depends(get_statistics_repository), id: int
):
    statistics: Optional[DBStatistics] = repository.get(id)
    return or_404(statistics)


@router.post("/", response_model=Statistics, status_code=201)
def create_statistics(
    *,
    _: bool = Depends(is_authenticated),
    repository: StatisticsRepository = Depends(get_statistics_repository),
    statistics: StatisticsUpdate,
):
    db_statistics: DBStatistics = DBStatistics(**statistics.dict())
    return repository.add(db_statistics)


@router.put("/{id}/", response_model=Statistics)
def update_statistics(
    *,
    _: bool = Depends(is_authenticated),
    repository: StatisticsRepository = Depends(get_statistics_repository),
    id: int,
    statistics_update: StatisticsUpdate,
):
    db_statistics: DBStatistics = or_404(repository.get(id))
    updated: DBStatistics = repository.update(
        db_statistics, statistics_update.dict(skip_defaults=True)
    )
    return updated


@router.delete("/{id}/")
def delete_statistics(
    *,
    _: bool = Depends(is_authenticated),
    repository: StatisticsRepository = Depends(get_statistics_repository),
    id: int,
):
    deleted: int = repository.delete(id)
    if deleted:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404)
