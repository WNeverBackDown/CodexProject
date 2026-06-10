from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.ai.drill_down.router import router as drill_router
from api.ai.router import router as ai_router
from api.auth.router import router as auth_router
from api.dashboard.router import router as dashboard_router
from api.mcp_router import router as mcp_router
from api.reports.router import router as reports_router
from api.rules.chain.router import router as chain_router
from api.user_portrait.behavior_config.router import router as portrait_config_router
from api.user_portrait.user_behavior.router import router as user_behavior_router
from common.scheduler import scheduler_manager
from common.utils.logger import logger
from common.utils.utils import ok
from config_env import settings
from database import SessionLocal, init_db
from seed_data import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)
    scheduler_manager.start()
    logger.info("DataPulse started")
    yield
    scheduler_manager.shutdown()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.cors_origins == ["*"] else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(ai_router)
app.include_router(drill_router)
app.include_router(chain_router)
app.include_router(reports_router)
app.include_router(portrait_config_router)
app.include_router(user_behavior_router)
app.include_router(mcp_router)


@app.get("/api/health")
def health() -> dict:
    return ok({"env": settings.env, "version": settings.app_version, "database": settings.database_url.split("://", 1)[0]})


@app.get("/")
def root() -> dict:
    return ok({"name": settings.app_name, "docs": "/docs", "frontend": "http://localhost:5173"})


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.env == "development")
