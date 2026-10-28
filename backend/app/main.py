from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import api, db

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db(db.get_db_path())
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="LeaveBot", lifespan=lifespan)
    # 先登記所有 /api 路由，最後才掛載靜態目錄，避免靜態頁攔截 API 路徑。
    app.include_router(api.router)
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
