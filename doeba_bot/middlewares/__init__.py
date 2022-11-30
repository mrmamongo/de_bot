from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .database import DBMiddleware
from doeba_bot.models.base import create_engine, create_tables


async def setup(dp: Dispatcher) -> None:
    engine = await create_engine()
    await create_tables(engine)
    dp.message.middleware.register(DBMiddleware(sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)))
