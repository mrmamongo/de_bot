from typing import Iterator

from aiogram import F
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from pyrate_limiter import RequestRate, Limiter, BucketFullException


class ComplexRequestRate:
    def __init__(self, *request_rates: RequestRate):
        self.request_rates = request_rates

    def __iter__(self) -> Iterator[RequestRate]:
        yield from iter(self.request_rates)


class OverflowFilter(BaseFilter):
    def __init__(
            self,
            request_rate: ComplexRequestRate | RequestRate,
            *separate_by: "F",
            limiter: Limiter | None = None,
            delay: bool = False,
            max_delay: int | float | None = None,
            raise_if_overflow: bool = False
    ):
        super().__init__()
        self.separate_by = separate_by
        if not limiter:
            if isinstance(request_rate, RequestRate):
                self.limiter = Limiter(request_rate)
            else:
                self.limiter = Limiter(*request_rate)
        self.delay = delay
        self.max_delay = max_delay
        self.raise_if_overflow = raise_if_overflow

    async def __call__(
            self,
            event: TelegramObject
    ) -> bool:
        keys = map(str, filter(None, [magic_filter.resolve for magic_filter in self.separate_by]))
        try:
            async with self.limiter.ratelimit(*keys, delay=self.delay, max_delay=self.max_delay):
                return True
        except BucketFullException as e:
            if self.raise_if_overflow:
                raise e
            return False
