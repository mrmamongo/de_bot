from aiogram import Router, types, F
from aiogram.filters.command import CommandStart
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from doeba_bot.models.user import User, Doc, Comment

router = Router()


@router.message(CommandStart())
async def start(message: types.Message, db: AsyncSession):
    async with db.begin():
        user = (await db.execute(select(User).where(User.id.__eq__(message.from_user.id)))).scalar_one_or_none()
        if user is None:
            user = User(id=message.from_user.id, username=message.from_user.username)
            db.add(user)
            await db.commit()

    logger.info("User {user} started bot", user=user.username)
    await message.answer(f"Hello, {user.username}! {message.from_user.id}")


@router.message(F.content_type.in_({'document', 'file'}))
async def doc(message: types.Message, db: AsyncSession):
    logger.info("Document from {user}: {doc} - {m}", user=message.from_user.username, doc=message.document.file_name,
                m=message.caption)

    user = (await db.execute(select(User).where(User.id.__eq__(message.from_user.id)))).scalar_one_or_none()
    if user is None:
        await message.answer("Авторизуйся, дебил")
        return
    d = Doc(name=message.document.file_name, url=message.document.file_id, author_id=user.id)
    d.comments.append(Comment(text=message.caption, author_id=user.id, doc_id=d.id))
    db.add(d)
    await db.commit()
    await message.answer("Документ добавлен")
