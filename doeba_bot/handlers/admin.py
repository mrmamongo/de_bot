from aiogram import Router, types, Bot, F
from aiogram.filters.command import CommandStart, Command
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import URLInputFile
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from doeba_bot.callback_data.doeba_callback import DoebaCallback
from doeba_bot.config import settings
from doeba_bot.models.user import Doc, Comment
from doeba_bot.states.doeba import DoebaState

router = Router()

help_message = "Чтобы получить список документов, напиши /poll"


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"Пивет, {message.from_user.username}! Я Бот-доёба, помогу тебе доебаться до студентов :) {help_message}")


@router.message(Command(commands=["poll"]))
async def msg(message: types.Message, db: AsyncSession):
    await message.answer("Посмотрим, что у нас там с документиками...")
    documents = (await db.execute(select(Doc).where(Doc.status == "new"))).fetchall()
    m = "\n".join([f"/doc_{d[0].id}" for d in documents])
    logger.info("Sent documents: {msg}", msg=m)
    await message.answer(
        text=f"Новые документы:\n{m}"
    )


@router.message(Text(startswith="/doc_"))
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
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.KeyboardButton(text="Ды",
                                         callback_data=DoebaCallback(result="yep", message_id=message.message_id,
                                                                     chat_id=message.from_user.id).pack()),
                    types.KeyboardButton(text="Ни",
                                         callback_data=DoebaCallback(result="nop", message_id=message.message_id,
                                                                     chat_id=message.from_user.id).pack()),
                ]
            ],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )


@router.callback_query(DoebaCallback.filter(F.result == "yep"))
async def write_doeba(query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(chat_id=query.from_user.id, text="Напиши свою доёбу")
    await state.set_state(DoebaState.writing)
    # await bot.send_message(chat_id=query.from_user.id, text="Ну и ладно")


@router.callback_query(DoebaCallback.filter(F.result == "nop"))
async def no_doeba(query: types.CallbackQuery, callback_data: DoebaCallback, bot: Bot):
    await bot.send_message(chat_id=query.from_user.id, text="Ну и ладно")
    await bot.delete_message(message_id=int(callback_data.message_id), chat_id=callback_data.chat_id)


@router.message(DoebaState.writing)
async def save_doeba(message: types.Message, db: AsyncSession, state: FSMContext):
    await message.answer(f"Доёба: {message.text}")
    new_comment = Comment(text=message.text, author_id=message.from_user.id, doc_id=(await state.get_data())["doc_id"])
    db.add(new_comment)
    await db.commit()
    await state.clear()


@router.message()
async def msg(message: types.Message):
    await message.answer(help_message)
