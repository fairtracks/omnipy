from typing import Any, cast, Coroutine

from aiohttp import ClientSession, TraceConfig
from aiolimiter import AsyncLimiter

DEFAULT_REQUESTS_PER_SECOND = 1


class RateLimitingClientSession(ClientSession):
    def __init__(self, requests_per_second: int = DEFAULT_REQUESTS_PER_SECOND, *args, **kwargs):
        trace_config = TraceConfig()
        trace_config.on_request_start.append(self._limit_request)
        super().__init__(*args, trace_configs=[trace_config], **kwargs)
        self._requests_per_second = requests_per_second

        # time_period is 2 seconds to allow for an initial burst of requests of size
        # `requests_per_second` to go through before rate limiting kicks in
        self._limiter = AsyncLimiter(requests_per_second, 2)

    async def _limit_request(self, *args, **kwargs):
        await self._limiter.acquire()

    @property
    def requests_per_second(self):
        return self._requests_per_second

    def __aenter__(self) -> 'Coroutine[Any, Any, RateLimitingClientSession]':
        return cast('Coroutine[Any, Any, RateLimitingClientSession]', super().__aenter__())
