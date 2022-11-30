from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from doeba_bot.models.base import create_tables


class DBMiddleware(BaseMiddleware):
    def __init__(self, connection_pool: sessionmaker):
        super().__init__()
        self.connection_pool = connection_pool

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        async with self.connection_pool() as db:
            data['db']: AsyncSession = db
            return await handler(event, data)
