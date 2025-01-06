import asyncio
from datetime import datetime
from types import TracebackType
from typing import cast

from aiohttp import ClientSession, TraceConfig
from aiolimiter import AsyncLimiter


class RateLimitingClientSession(ClientSession):
    """
    A ClientSession that limits the number of requests made per time period, allowing an initial
    burst of requests to go through before rate limiting kicks in for the rest.
    """
    def __init__(self, requests_per_time_period: float, time_period_in_secs: float, *args,
                 **kwargs) -> None:
        trace_config = TraceConfig()
        trace_config.on_request_start.append(self._limit_request)
        super().__init__(*args, trace_configs=[trace_config], **kwargs)

        self._requests_per_time_period = requests_per_time_period
        self._time_period_in_secs = time_period_in_secs

        self._limiter = AsyncLimiter(self._requests_per_time_period, self._time_period_in_secs)

        # To allow for an initial burst of requests of size `requests_per_time_period / 2 + 1`
        # to go through before rate limiting kicks in for the rest
        self._burst_size = self._requests_per_time_period / 2 + 1
        self._limiter.max_rate = self._burst_size
        self._cur_delay_secs: float = 0
        self._num_requests: int = 0
        self._first_submit_time: datetime | None = None

    async def _limit_request(self, *args, **kwargs):

        request_num = self._num_requests
        self._num_requests += 1

        submit_time = datetime.now()
        if self._first_submit_time is None:
            self._first_submit_time = submit_time

        await self._limiter.acquire()

        submit_time_delta = (submit_time - self._first_submit_time).total_seconds()
        if submit_time_delta > self._time_period_in_secs:
            # Resetting the rate limiter for the next batch of requests
            self._first_submit_time = submit_time
            self._cur_delay_secs = 0
            self._num_requests = 1
            request_num = 0

        # Adding a delay to compensate for the filling of the leaky bucket, which is not accounted
        # for in the AsyncLimiter. This is to allow for an initial burst of requests to go through
        # while not exceeding the rate limit for the first time period
        if self._burst_size <= request_num <= self._requests_per_time_period:
            self._cur_delay_secs += 1 / self.requests_per_second

        if self._cur_delay_secs > 0:
            await asyncio.sleep(self._cur_delay_secs)

        # print(f'Request number: {request_num}, Actual request time: {datetime.now()}')

    @property
    def requests_per_second(self) -> float:
        return self._requests_per_time_period / self._time_period_in_secs

    async def __aenter__(self) -> 'RateLimitingClientSession':
        return cast(RateLimitingClientSession, await super().__aenter__())

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
