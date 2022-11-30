from aiogram import types
from aiogram.dispatcher.filters import BaseFilter
from pydantic.fields import Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from doeba_bot.models.user import User


class AdminFilter(BaseFilter):
    connection: AsyncConnection | None = Field(default=None, alias='connection')

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, connection: AsyncConnection):
        super().__init__()
        self.connection = connection

    async def __call__(self,
                       message: types.Message) -> bool:
        async with self.connection.begin():
            user = (await self.connection.execute(select(User.is_admin).where(User.id.__eq__(message.from_user.id)))) \
                .one_or_none()
            if user is None:
                return False
            return user.is_admin
