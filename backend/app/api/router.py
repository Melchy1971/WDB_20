from fastapi import APIRouter

from app.api.routes.filesystem import router as filesystem_router
from app.api.routes.health import router as health_router
from app.api.routes.import_jobs import import_jobs_router, sources_import_router
from app.api.routes.import_runs import router as import_runs_router
from app.api.routes.persist import router as persist_router
from app.api.routes.settings import router as settings_router
from app.api.routes.sources import router as sources_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(filesystem_router)
api_router.include_router(sources_router)
api_router.include_router(sources_import_router)
api_router.include_router(import_jobs_router)
api_router.include_router(import_runs_router)
api_router.include_router(persist_router)
api_router.include_router(settings_router)
