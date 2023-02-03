import aiojobs as aiojobs
import aioredis as aioredis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp import web
from aioredis import Redis
from loguru import logger

from doeba_bot import webhook_handlers
from doeba_bot.handlers import setup as handlers
from doeba_bot.middlewares import setup as middlewares
from doeba_bot.filters import setup as filters
from doeba_bot.config import settings


async def on_startup(app: web.Application):
    await handlers(dp)
    await middlewares(dp)
    filters(dp)

    logger.info("Configuring Webhook URL to: {url}", url=settings.telegram.WEBHOOK_URL)
    await bot.set_webhook(settings.telegram.WEBHOOK_URL + f"/tg/bot/bot{settings.telegram.TOKEN}")
    logger.info("Started bot on {url}:{port}", url=settings.web.HOST, port=settings.web.PORT)


async def on_shutdown(app: web.Application):
    await dp.storage.close()
    await bot.close()


async def create_redis(url: str) -> Redis:
    return await aioredis.from_url(url)


async def init_app() -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [
        (f"/tg", webhook_handlers.tg_updates_app)
    ]
    for prefix, subapp in subapps:
        subapp['bot'] = bot
        subapp['dp'] = dp
        subapp['scheduler'] = scheduler
        app.add_subapp(prefix, subapp)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    bot = Bot(
        settings.telegram.token,
        parse_mode="HTML"
    )
    if settings.telegram.get("REDIS_URL", None) is not None:
        storage = RedisStorage(redis=create_redis(settings.telegram.REDIS_URL))
    else:
        storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    web.run_app(init_app(), host=settings.web.HOST, port=settings.web.PORT)
