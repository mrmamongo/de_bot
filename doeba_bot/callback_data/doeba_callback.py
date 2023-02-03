from aiogram.filters.callback_data import CallbackData


class DoebaCallback(CallbackData, prefix="doeb"):
    result: str
    message_id: str
    chat_id: str
