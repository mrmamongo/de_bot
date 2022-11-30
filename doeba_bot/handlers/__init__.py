from aiogram import Dispatcher, Router
from sqlalchemy.ext.asyncio import create_async_engine

from .user import router as user_router
from .admin import router as admin_router
from ..config import settings
from ..filters.admin import AdminFilter


async def setup(dp: Dispatcher):
    router = Router()
    admin_router.message.filter(AdminFilter(
        connection=await create_async_engine(settings.DATABASE_URL).connect()
    ))
    router.include_router(admin_router)
    router.include_router(user_router)
    dp.include_router(router)
