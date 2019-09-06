from fastapi import APIRouter

from rfhub2.api.endpoints import collections, healthcheck, keywords, version

api_router = APIRouter()
api_router.include_router(healthcheck.router, prefix="/health", tags=["healthcheck"])
api_router.include_router(
    collections.router, prefix="/collections", tags=["collections"]
)
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(version.router, prefix="/version", tags=["version"])
