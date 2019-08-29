from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from rfhub2 import config
from rfhub2.api.router import api_router
from rfhub2.api.middleware.db_session_middleware import DbSessionMiddleware
from rfhub2.ui.ui_router import router as ui_router
from rfhub2.utils import abs_path
from rfhub2.version import version


def create_app() -> FastAPI:
    app = FastAPI(title=config.APP_TITLE, version=version)
    app.mount("/static", StaticFiles(directory=abs_path("static")), name="static")
    app.include_router(ui_router)
    app.include_router(api_router, prefix="/api/v1")
    app.add_middleware(CORSMiddleware, allow_origins=["*"])
    app.add_middleware(DbSessionMiddleware)
    return app
