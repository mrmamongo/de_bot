from aiogram import Router, types, Bot
from aiogram.dispatcher.filters.command import CommandStart, Command
from aiogram.dispatcher.filters.text import Text
from aiogram.types import URLInputFile
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from doeba_bot.config import settings
from doeba_bot.models.user import Doc, Comment

router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer(f"Пивет, {message.from_user.username}! Я Бот-доёба, помогу тебе доебаться до студентов :)")


@router.message(Command(commands=["poll"]))
async def msg(message: types.Message, db: AsyncSession):
    await message.answer("Посмотрим, что у нас там с документиками...")
    documents = (await db.execute(select(Doc).where(Doc.status == "new"))).fetchall()
    m = "\n".join([f"/doc_{d[0].id}" for d in documents])
    logger.info("Sent documents: {msg}", msg=m)
    await message.answer(
        text=f"Новые документы:\n{m}"
    )


@router.message(Text(text_startswith="/doc_"))
async def doc(message: types.Message, db: AsyncSession, bot: Bot):
    doc_id = int(message.text.split("_")[1])
    d: Doc | None = (await db.execute(select(Doc).where(Doc.id == doc_id))).one_or_none()
    if d is None:
        await message.answer("Документ не найден")
        return
    document = URLInputFile(
        f"https://api.telegram.org/file/bot{settings.telegram.token}/{d[0].url}",
        filename=f"{d[0].name}",
    )
    comments = (await db.execute(
        select(Comment.text).where(Comment.doc_id == doc_id and Comment.author_id != message.from_user.id))).fetchall()
    comments = "\n".join([f"{c[0]}" for c in comments])
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"Документ: {d[0].name}\nКомментарии:\n{comments}",
    )
    await bot.send_document(
        chat_id=message.from_user.id,
        document=document
    )
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"Доебаться?",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="Да", callback_data="yes"),
                    types.KeyboardButton(text="Нет", callback_data="no"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )
