from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


async def create_engine() -> AsyncEngine:
    from doeba_bot.config import settings

    return create_async_engine(
        settings.DATABASE_URL,
        future=True,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
