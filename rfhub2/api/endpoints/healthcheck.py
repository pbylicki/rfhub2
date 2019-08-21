from fastapi import APIRouter, Depends
from starlette.responses import Response

from rfhub2.api.utils.db import db_healthcheck
from rfhub2.model import Healthcheck

router = APIRouter()


@router.get("/", response_model=Healthcheck)
def healthcheck(response: Response, db_status: bool = Depends(db_healthcheck)):
    if db_status:
        return Healthcheck(**{"db": "ok"})
    else:
        response.status_code = 503
        return Healthcheck(**{"db": "failure"})
