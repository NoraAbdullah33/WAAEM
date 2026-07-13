"""Async SQLAlchemy engine, session factory and declarative base."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# `check_same_thread` is a SQLite-only connect arg.
connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=not settings.is_sqlite,
    connect_args=connect_args,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a transactional session."""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create tables for local/dev (production uses Alembic migrations)."""
    from app.db import models  # noqa: F401 — ensure models are imported

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
