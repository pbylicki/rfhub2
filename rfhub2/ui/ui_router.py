from fastapi import APIRouter
from starlette.responses import FileResponse

from rfhub2.utils import abs_path

router = APIRouter()


@router.get("/")
@router.get("/search/")
@router.get("/keywords/{collection_id}/")
@router.get("/keywords/{collection_id}/{keyword_id}/")
async def home():
    return FileResponse(abs_path("templates", "index.html"), media_type="text/html")
