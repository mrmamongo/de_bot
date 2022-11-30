import loguru
from aiogram import Bot, Dispatcher, types
from aiohttp import web

tg_updates_app = web.Application()


async def proceed_update(req: web.Request):
    upds = [types.Update(**(await req.json()))]
    Bot.set_current(req.app['bot'])
    bot: Bot = req.app['bot']
    dp: Dispatcher = req.app['dp']
    for upd in upds:
        await dp.feed_update(bot, upd)


async def execute(req: web.Request) -> web.Response:
    loguru.logger.debug("Got update from Telegram")
    await req.app['scheduler'].spawn(proceed_update(req))
    return web.Response()


tg_updates_app.add_routes([web.post('/bot/bot{token}', execute)])