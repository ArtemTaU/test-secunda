from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from .config import Settings
from .logging import setup_logging
from app.infrastructure.repos.session import Base
from app.infrastructure.repos.utils import build_db_url
from app.infrastructure.repos import async_session, async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = Settings()
    settings = app.state.settings
    settings.db_url = build_db_url(settings)

    app.state.logger = setup_logging(app.state.settings.log_level)
    log = app.state.logger

    log.info("Creating SQLAlchemy engine...")
    try:
        aengine = async_engine(settings.db_url)
    except Exception:
        log.exception("Failed to create SQLAlchemy engine")
        raise
    else:
        log.info("SQLAlchemy engine created")

    log.info("Creating SQLAlchemy session maker...")
    try:
        app.state.session_maker = async_session(aengine)
    except Exception:
        log.exception("Failed to create session maker")
        raise
    else:
        log.info("Session maker created")

    async with aengine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    log.info("DB ping OK")

    async with aengine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        await aengine.dispose()

