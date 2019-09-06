from fastapi import APIRouter

from rfhub2.config import APP_TITLE
from rfhub2.model import VersionInfo
from rfhub2.version import version

router = APIRouter()


@router.get("/", response_model=VersionInfo)
def healthcheck():
    return VersionInfo(**{"title": APP_TITLE, "version": version})
