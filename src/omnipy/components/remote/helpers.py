"""Async HTTP helpers for rate limiting and retry strategy selection."""

import asyncio
from collections import deque
from datetime import datetime
import math
from types import TracebackType
from typing import cast

from omnipy.shared.enums.data import BackoffStrategy

from .lazy_import import (
    ClientSession,
    ExponentialRetry,
    FibonacciRetry,
    JitterRetry,
    RandomRetry,
    TraceConfig,
)

DEFAULT_BURST_RATIO = 0.5

# Tolerance for comparing times that are computed by floating-point arithmetic. For instance, a
# start that is planned for the moment an earlier start leaves the time period may come out a
# fraction of a nanosecond early. Times this close are treated as equal
_EPS = 1e-9


class RequestPacer:
    """
    Decides when rate-limited requests may start, for requests handled one at a time in order.

    Guarantees, for ``requests_per_time_period`` (R) requests per ``time_period_in_secs`` (P) and a
    burst size B:

    - at most R requests start within any time period, wherever the period is placed;
    - at most B + (R/P)·t requests start within any interval of length t (a leaky-bucket bound);
    - while requests are waiting, they keep being started: the pace may slow down after a burst,
      but there are no pauses.

    While fewer than B requests have started within the last time period, a request starts as soon
    as it is ready (a burst). Otherwise, the requests are spaced out. The spacing is the largest of
    ``(leaves - previous_start) / (free + m)`` over the starts within the last time period, where
    ``leaves`` is the time the m-th of these starts leaves the time period and ``free`` is the
    number of further starts the time period allows. This is the fastest even pace from the
    previous start that never needs to wait for a start to leave the time period.

    The spacing stays the same until the start that set it has left the time period, a request
    starts later than the spacing allows (it was not ready), or a burst happens. It is only
    calculated anew at these points. Among starts giving the same spacing, the one that leaves
    the time period last sets it, so that it holds as long as possible.

    The class has no clock: callers pass the times. See
    docs/agents/technical/specs/2026-10-24-rate-limiter-pacing-design.md for the design.
    """

    def __init__(
        self,
        requests_per_time_period: int,
        time_period_in_secs: float,
        burst_ratio: float = DEFAULT_BURST_RATIO,
    ) -> None:
        if (
            isinstance(requests_per_time_period, bool)
            or not isinstance(requests_per_time_period, int)
            or requests_per_time_period < 1
        ):
            raise ValueError(
                f'requests_per_time_period must be a positive integer, '
                f'not {requests_per_time_period!r}'
            )
        if not time_period_in_secs > 0:
            raise ValueError(f'time_period_in_secs must be positive, not {time_period_in_secs!r}')
        if not 0 < burst_ratio < 1:
            raise ValueError(f'burst_ratio must be between 0 and 1, not {burst_ratio!r}')

        self._requests_per_time_period = requests_per_time_period
        self._time_period_in_secs = time_period_in_secs
        self._burst_size = max(1, math.floor(burst_ratio * requests_per_time_period + _EPS))

        # Starts within the last time period, in order
        self._starts: deque[float] = deque()
        self._last_start: float | None = None

        # The current spacing, and the time the start that set it leaves the time period
        self._spacing: float | None = None
        self._spacing_valid_until = 0.0

        # Whether the planned request was ready only after the spacing allowed it to start
        self._planned_request_is_late = False

    @property
    def requests_per_time_period(self) -> int:
        return self._requests_per_time_period

    @property
    def time_period_in_secs(self) -> float:
        return self._time_period_in_secs

    @property
    def burst_size(self) -> int:
        return self._burst_size

    @property
    def requests_per_second(self) -> float:
        """Return the configured steady-state request rate."""
        return self._requests_per_time_period / self._time_period_in_secs

    def plan_start(self, ready_time: float) -> float:
        """Return the start time for the next request, which is ready at ``ready_time``.

        Planning the same request again gives the same start time, so a request that is cancelled
        before it starts does not affect the following ones. Report the actual start with
        ``record_start()``.
        """
        prev = self._last_start
        now = ready_time if prev is None else max(ready_time, prev)

        if prev is None or self._num_starts_in_time_period(now) < self._burst_size:
            self._spacing = None
            self._planned_request_is_late = False
            return now

        if (
            self._spacing is None
            or prev >= self._spacing_valid_until - _EPS
            or now > prev + self._spacing + _EPS
        ):
            self._spacing, self._spacing_valid_until = self._calculate_spacing(now, prev)

        self._planned_request_is_late = now > prev + self._spacing + _EPS
        return max(now, prev + self._spacing)

    def record_start(self, start_time: float) -> None:
        """Record that the planned request has started at ``start_time``.

        The start may be a little later than planned, e.g. when the event loop is busy. The
        current spacing is then kept, which only paces the following requests a little slower
        than needed.
        """
        if self._planned_request_is_late:
            # The request was not ready in time, so its start is the new reference point
            self._spacing = None
            self._planned_request_is_late = False

        self._starts.append(start_time)
        self._last_start = start_time
        while self._starts and not self._is_in_time_period(self._starts[0], start_time):
            self._starts.popleft()

    def _is_in_time_period(self, start: float, now: float) -> bool:
        return start > now - self._time_period_in_secs + _EPS

    def _num_starts_in_time_period(self, now: float) -> int:
        num_left = 0
        for start in self._starts:
            if self._is_in_time_period(start, now):
                break
            num_left += 1
        return len(self._starts) - num_left

    def _calculate_spacing(self, now: float, prev: float) -> tuple[float, float]:
        in_time_period = [start for start in self._starts if self._is_in_time_period(start, now)]
        num_free = self._requests_per_time_period - len(in_time_period)

        spacing = -math.inf
        valid_until = prev
        for m, start in enumerate(in_time_period, start=1):
            leaves = start + self._time_period_in_secs
            candidate = (leaves - prev) / (num_free + m)
            # Among equal candidates, the start that leaves last sets the spacing
            if candidate >= spacing - _EPS:
                spacing = max(spacing, candidate)
                valid_until = leaves
        return spacing, valid_until


class RateLimitingClientSession(ClientSession):
    """
    A ClientSession that limits the number of requests made per time period, allowing an initial
    burst of requests to go through before rate limiting kicks in for the rest.
    """

    def __init__(
        self, requests_per_time_period: float, time_period_in_secs: float, *args, **kwargs
    ) -> None:
        from .lazy_import import AsyncLimiter

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
        """Return the configured steady-state request rate."""

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


BACKOFF_STRATEGY_2_RETRY_CLS = {
    BackoffStrategy.EXPONENTIAL: ExponentialRetry,
    BackoffStrategy.JITTER: JitterRetry,
    BackoffStrategy.FIBONACCI: FibonacciRetry,
    BackoffStrategy.RANDOM: RandomRetry,
}
